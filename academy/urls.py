from django.urls import path
from .views import (
    StudentStatsAPIView,
    TrainerListCreateAPIView,
    TrainerDetailAPIView,
    StudentListCreateAPIView,
    StudentDetailAPIView,
    AttendanceListCreateAPIView,
    AttendanceDetailAPIView,          
    QuickMarkAttendanceAPIView,        
    AttendanceRecordsAPIView,          
    ExportStudentAttendanceAPIView,    
)

app_name = 'academy'

urlpatterns = [
    # Trainers
    path('trainers/', TrainerListCreateAPIView.as_view(), name='trainer-list-create'),
    path('trainers/<int:pk>/', TrainerDetailAPIView.as_view(), name='trainer-detail'),

    # Students
    path('students/stats/', StudentStatsAPIView.as_view(), name='student-stats'),
    path('students/', StudentListCreateAPIView.as_view(), name='student-list-create'),
    path('students/<int:pk>/', StudentDetailAPIView.as_view(), name='student-detail'),

    # Attendance
    path('attendance/', AttendanceListCreateAPIView.as_view(), name='attendance-list-create'),
    path('attendance/detail/', AttendanceDetailAPIView.as_view(), name='attendance-detail'),  # fixed
    path('attendance/quick-mark/', QuickMarkAttendanceAPIView.as_view(), name='quick-mark-attendance'),
    path('students/<int:student_id>/attendance-records/', AttendanceRecordsAPIView.as_view(), name='attendance-records'),
    path('students/<int:student_id>/export-attendance/', ExportStudentAttendanceAPIView.as_view(), name='export-student-attendance'),
]
