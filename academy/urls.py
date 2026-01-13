from django.urls import path
from .views import (
    TrainerListCreateAPIView,
    TrainerDetailAPIView,
    StudentListCreateAPIView,
    StudentDetailAPIView,
    AttendanceListCreateAPIView
)

urlpatterns = [
    path('trainers/', TrainerListCreateAPIView.as_view(), name='trainer-list-create'),
    path('trainers/<int:pk>/', TrainerDetailAPIView.as_view(), name='trainer-detail'),
    path('students/', StudentListCreateAPIView.as_view(), name='student-list-create'),
    path('students/<int:pk>/', StudentDetailAPIView.as_view(), name='student-detail'),
    path('attendance/', AttendanceListCreateAPIView.as_view(), name='attendance-list-create'),
]
