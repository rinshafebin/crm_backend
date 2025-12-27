from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Task, TaskUpdate
from .serializers import TaskSerializer, TaskUpdateSerializer

class TaskListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role in ['MEDIA', 'ADM_MANAGER', 'ADM_EXEC']:
            tasks = Task.objects.filter(assigned_to=user)
        elif user.role in ['ADMIN', 'BUSINESS_HEAD', 'OPS']:
            tasks = Task.objects.filter(assigned_by=user)
        else:
            tasks = Task.objects.none()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.role not in ['ADMIN', 'BUSINESS_HEAD', 'OPS']:
            return Response(
                {"detail": "You do not have permission to create tasks."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(assigned_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        try:
            task = Task.objects.get(pk=pk)
            # Ensure user has permission to view
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
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def put(self, request, pk):
        task = self.get_object(pk, request.user)
        if not task:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        # Only admin/manager can update the task
        if request.user.role not in ['ADMIN', 'BUSINESS_HEAD', 'OPS']:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        task = self.get_object(pk, request.user)
        if not task:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        # Only admin/manager can delete
        if request.user.role not in ['ADMIN', 'BUSINESS_HEAD', 'OPS']:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
