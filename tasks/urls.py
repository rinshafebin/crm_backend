from django.urls import path
from .views import (
    TaskStatsAPIView,
    EmployeeListAPIView,
    TaskListCreateAPIView,
    TaskDetailAPIView,
    TaskUpdateListCreateAPIView,
    TasksAssignedByMeAPIView,
    TaskStatusUpdateAPIView,
    UpcomingTasksAPIView
)

urlpatterns = [
    path('tasks/stats/', TaskStatsAPIView.as_view(), name='task-stats'),
    path('employees/', EmployeeListAPIView.as_view(), name='employee-list'),
    path('tasks/', TaskListCreateAPIView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskDetailAPIView.as_view(), name='task-detail'),
    path('tasks/<int:task_id>/updates/', TaskUpdateListCreateAPIView.as_view(), name='task-updates'),
    path('tasks/assigned-by-me/', TasksAssignedByMeAPIView.as_view(), name='tasks-assigned-by-me'),
    path('tasks/<int:pk>/status/', TaskStatusUpdateAPIView.as_view(), name='task-status-update'),
    path('upcoming/', UpcomingTasksAPIView.as_view(), name='upcoming-tasks'),
]
