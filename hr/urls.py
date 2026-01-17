from django.urls import path
from .views import PenaltyListCreateAPI, PenaltyDetailAPI, AttendanceDocumentAPI, AttendanceDocumentDeleteAPI

urlpatterns = [
    path("penalties/", PenaltyListCreateAPI.as_view()),
    path("penalties/<int:pk>/", PenaltyDetailAPI.as_view()),
    path("attendance/", AttendanceDocumentAPI.as_view()),
    path("attendance/<int:pk>/", AttendanceDocumentDeleteAPI.as_view()),
]
