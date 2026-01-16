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
from .permissions import IsTaskAssigner
from rest_framework.exceptions import PermissionDenied

User = get_user_model()


#  Pagination 
class TaskPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

#  Task Stats
class TaskStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role in TASK_ASSIGNEES:
            qs = Task.objects.filter(assigned_to=user)
        elif user.role in TASK_ASSIGNERS:
            qs = Task.objects.filter(assigned_by=user)
        else:
            qs = Task.objects.none()

        stats = qs.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status='PENDING')),
            in_progress=Count('id', filter=Q(status='IN_PROGRESS')),
            completed=Count('id', filter=Q(status='COMPLETED')),
            overdue=Count('id', filter=Q(status='OVERDUE')),
        )

        return Response({
            "total": stats["total"],
            "pending": stats["pending"],
            "in_progress": stats["in_progress"],
            "completed": stats["completed"],
            "overdue": stats["overdue"],
        })


#  Employee List 
class EmployeeListAPIView(generics.ListAPIView):
    permission_classes = [IsTaskAssigner]
    queryset = User.objects.filter(is_active=True)
    serializer_class = EmployeeSerializer




#  Task List / Create 
from .permissions import IsTaskAssigner, TASK_ASSIGNERS, TASK_ASSIGNEES

class TaskListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    pagination_class = TaskPagination

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsTaskAssigner()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = Task.objects.select_related("assigned_to", "assigned_by")

        if user.role in TASK_ASSIGNEES:
            return qs.filter(assigned_to=user).order_by("-created_at")

        if user.role in TASK_ASSIGNERS:
            return qs.filter(assigned_by=user).order_by("-created_at")

        return Task.objects.none()

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)


#  Task Detail / Update / Delete 
class TaskDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsTaskAssigner()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = Task.objects.select_related("assigned_to", "assigned_by")

        if user.role in TASK_ASSIGNEES:
            return qs.filter(assigned_to=user)

        if user.role in TASK_ASSIGNERS:
            return qs.filter(assigned_by=user)

        return Task.objects.none()


#  Task Updates 
class TaskUpdateListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskUpdateSerializer

    def get_queryset(self):
        return TaskUpdate.objects.filter(
            task_id=self.kwargs["task_id"]
        ).order_by("-created_at")

    def perform_create(self, serializer):
        task = get_object_or_404(Task, pk=self.kwargs["task_id"])

        if task.assigned_to != self.request.user:
            raise PermissionDenied("Only assigned employee can update this task.")

        serializer.save(
            task=task,
            updated_by=self.request.user,
            previous_status=task.status
        )

        task.status = serializer.validated_data["new_status"]
        task.save(update_fields=["status", "updated_at"])



#  Task Dashboard
class TaskDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        qs = (
            Task.objects.filter(assigned_to=user)
            if user.role in TASK_ASSIGNEES
            else Task.objects.filter(assigned_by=user)
        )
        return Response({
            "total": qs.count(),
            "pending": qs.filter(status="PENDING").count(),
            "in_progress": qs.filter(status="IN_PROGRESS").count(),
            "completed": qs.filter(status="COMPLETED").count(),
            "overdue": qs.filter(status="OVERDUE").count(),
        })


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
        qs = Task.objects.filter(
            assigned_to=request.user,
            status__in=["PENDING", "IN_PROGRESS", "OVERDUE"],
            deadline__gte=timezone.now().date()
        ).order_by("-priority", "deadline")[:5]

        serializer = UpcomingTaskSerializer(qs, many=True)
        return Response(serializer.data)
