from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from .models import Task, TaskUpdate
from .serializers import TaskSerializer, TaskUpdateSerializer,EmployeeSerializer, UpcomingTaskSerializer
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from django.utils import timezone

User = get_user_model()


#  Pagination 
class TaskPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


#  Employee List 
class EmployeeListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = EmployeeSerializer  



#  Task List / Create 
class TaskListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    pagination_class = TaskPagination

    def get_queryset(self):
        user = self.request.user
        qs = Task.objects.select_related('assigned_to', 'assigned_by').all()
        if user.role in ['MEDIA', 'ADM_MANAGER', 'ADM_EXEC']:
            return qs.filter(assigned_to=user).order_by('-created_at')
        elif user.role in ['ADMIN', 'BUSINESS_HEAD', 'OPS', 'GENERAL_MANAGER']:
            return qs.filter(assigned_by=user).order_by('-created_at')
        return Task.objects.none()

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        stats = qs.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status='PENDING')),
            in_progress=Count('id', filter=Q(status='IN_PROGRESS')),
            completed=Count('id', filter=Q(status='COMPLETED')),
            overdue=Count('id', filter=Q(status='OVERDUE')),
        )

        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        response = self.get_paginated_response(serializer.data)
        response.data['stats'] = stats
        return response

    def create(self, request, *args, **kwargs):
        if request.user.role not in ['ADMIN', 'BUSINESS_HEAD', 'OPS', 'GENERAL_MANAGER']:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(assigned_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


#  Task Detail / Update / Delete 
class TaskDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        user = self.request.user
        qs = Task.objects.select_related('assigned_to', 'assigned_by').all()
        if user.role in ['MEDIA', 'ADM_MANAGER', 'ADM_EXEC']:
            return qs.filter(assigned_to=user)
        elif user.role in ['ADMIN', 'BUSINESS_HEAD', 'OPS', 'GENERAL_MANAGER']:
            return qs.filter(assigned_by=user)
        return Task.objects.none()

    def update(self, request, *args, **kwargs):
        if request.user.role not in ['ADMIN', 'BUSINESS_HEAD', 'OPS', 'GENERAL_MANAGER']:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.role not in ['ADMIN', 'BUSINESS_HEAD', 'OPS', 'GENERAL_MANAGER']:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


#  Task Updates 
class TaskUpdateListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskUpdateSerializer

    def get_queryset(self):
        task_id = self.kwargs.get('task_id')
        return TaskUpdate.objects.filter(task_id=task_id).order_by('-created_at')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        task_id = self.kwargs.get('task_id')
        task = get_object_or_404(Task, pk=task_id)
        context['task'] = task
        return context

    def perform_create(self, serializer):
        task = self.get_serializer_context()['task']
        if self.request.user != task.assigned_to:
            raise PermissionError("Only the assigned user can update this task.")

        serializer.save(
            task=task,
            updated_by=self.request.user,
            previous_status=task.status
        )

        # Sync task status
        task.status = serializer.validated_data['new_status']
        task.save(update_fields=['status', 'updated_at'])


#  Task Dashboard \
class TaskDashboardAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        qs = Task.objects.filter(assigned_to=user) if user.role in ['MEDIA', 'ADM_MANAGER', 'ADM_EXEC'] else Task.objects.filter(assigned_by=user)

        data = {
            "total": qs.count(),
            "pending": qs.filter(status='PENDING').count(),
            "in_progress": qs.filter(status='IN_PROGRESS').count(),
            "completed": qs.filter(status='COMPLETED').count(),
            "overdue": qs.filter(status='OVERDUE').count(),
        }
        return Response(data)


#  Tasks Assigned By Me 
class TasksAssignedByMeAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role not in ['ADMIN', 'BUSINESS_HEAD', 'OPS', 'GENERAL_MANAGER']:
            return Task.objects.none()
        return Task.objects.filter(assigned_by=user).select_related('assigned_to', 'assigned_by').order_by('-created_at')


#  Task Status Update 
class TaskStatusUpdateAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskUpdateSerializer

    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)

        if request.user != task.assigned_to:
            return Response({"detail": "Only assigned user can change status."}, status=status.HTTP_403_FORBIDDEN)

        new_status = request.data.get("status")
        notes = request.data.get("notes", "")

        if new_status not in dict(Task.STATUS_CHOICES):
            return Response({"detail": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

        TaskUpdate.objects.create(
            task=task,
            updated_by=request.user,
            previous_status=task.status,
            new_status=new_status,
            notes=notes
        )

        task.status = new_status
        task.save(update_fields=['status', 'updated_at'])

        return Response({"detail": "Status updated successfully"})


class UpcomingTasksAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()

        # Base queryset: tasks assigned to current user
        qs = Task.objects.filter(
            assigned_to=user,
            status__in=["PENDING", "IN_PROGRESS", "OVERDUE"],
        )

        # Optional: limit upcoming window (today + next 7 days)
        qs = qs.filter(deadline__gte=today)

        # Order by priority then deadline
        qs = qs.order_by("-priority", "deadline")[:5]

        serializer = UpcomingTaskSerializer(qs, many=True)
        return Response(serializer.data)