from django.urls import path
from .views import (
    TaskListCreateAPIView,
    TaskDetailAPIView,
    TaskUpdateListCreateAPIView,
    TaskDashboardAPIView,
    TasksAssignedByMeAPIView,
    TaskStatusUpdateAPIView,
)

urlpatterns = [
    path('tasks/', TaskListCreateAPIView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskDetailAPIView.as_view(), name='task-detail'),
    path('tasks/<int:task_id>/updates/', TaskUpdateListCreateAPIView.as_view(), name='task-update-list-create'),
    path('tasks/dashboard/', TaskDashboardAPIView.as_view(), name='task-dashboard'),
    path('tasks/assigned-by-me/', TasksAssignedByMeAPIView.as_view(), name='tasks-assigned-by-me'),
    path('tasks/<int:pk>/update-status/', TaskStatusUpdateAPIView.as_view(), name='task-status-update'),
]
