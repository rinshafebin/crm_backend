from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Task, TaskUpdate
from .serializers import TaskSerializer, TaskUpdateSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class EmployeeListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all().values(
            'id','username','role'
        )
        return Response(users)


# --------------------- Task List / Create ---------------------

class TaskListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role in ['MEDIA', 'ADM_MANAGER', 'ADM_EXEC']:
            tasks = Task.objects.filter(assigned_to=user)
        elif user.role in ['ADMIN', 'BUSINESS_HEAD', 'OPS', 'GENERAL_MANAGER']:
            tasks = Task.objects.filter(assigned_by=user)
        else:
            tasks = Task.objects.none()

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        print(request.data)
        if request.user.role not in ['ADMIN', 'BUSINESS_HEAD', 'OPS', 'GENERAL_MANAGER', 'ADM_MANAGER']:
            return Response(
                {"detail": "You do not have permission to create tasks."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TaskSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save(assigned_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# --------------------- Task Detail ---------------------

class TaskDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            task = Task.objects.get(pk=pk)

            if user.role in ['MEDIA', 'ADM_MANAGER', 'ADM_EXEC'] and task.assigned_to != user:
                return None

            if user.role in ['ADMIN', 'BUSINESS_HEAD', 'OPS'] and task.assigned_by != user:
                return None

            return task
        except Task.DoesNotExist:
            return None

    def get(self, request, pk):
        task = self.get_object(pk, request.user)
        if not task:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(TaskSerializer(task).data)

    def put(self, request, pk):
        if request.user.role not in ['ADMIN', 'BUSINESS_HEAD', 'OPS']:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        task = self.get_object(pk, request.user)
        if not task:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(
            task,
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if request.user.role not in ['ADMIN', 'BUSINESS_HEAD', 'OPS']:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        task = self.get_object(pk, request.user)
        if not task:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# --------------------- Task Updates ---------------------
class TaskUpdateListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        updates = TaskUpdate.objects.filter(task_id=task_id)
        return Response(TaskUpdateSerializer(updates, many=True).data)

    def post(self, request, task_id):
        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            return Response({"detail": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user != task.assigned_to:
            return Response(
                {"detail": "Only the assigned user can update this task."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TaskUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                task=task,
                updated_by=request.user,
                previous_status=task.status
            )

            # Sync task status
            task.status = serializer.validated_data['new_status']
            task.save(update_fields=['status', 'updated_at'])

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role in ['MEDIA', 'ADM_MANAGER', 'ADM_EXEC']:
            qs = Task.objects.filter(assigned_to=user)
        else:
            qs = Task.objects.filter(assigned_by=user)

        data = {
            "total": qs.count(),
            "pending": qs.filter(status='PENDING').count(),
            "in_progress": qs.filter(status='IN_PROGRESS').count(),
            "completed": qs.filter(status='COMPLETED').count(),
            "overdue": qs.filter(status='OVERDUE').count(),
        }

        return Response(data)
class TasksAssignedByMeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in ['ADMIN', 'BUSINESS_HEAD', 'OPS']:
            return Response(
                {"detail": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN
            )

        tasks = Task.objects.filter(assigned_by=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    
class TaskStatusUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({"detail": "Task not found."}, status=404)

        if request.user != task.assigned_to:
            return Response(
                {"detail": "Only assigned user can change status."},
                status=403
            )

        new_status = request.data.get("status")
        notes = request.data.get("notes", "")

        if new_status not in dict(Task.STATUS_CHOICES):
            return Response(
                {"detail": "Invalid status."},
                status=400
            )

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

class TaskUpdateListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        updates = TaskUpdate.objects.filter(task_id=task_id)
        serializer = TaskUpdateSerializer(updates, many=True)
        return Response(serializer.data)
