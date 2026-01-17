from django.urls import path
from .views import (
    RecentActivitiesAPIView,
    StaffByTeamView,
    StaffListView,
    StaffDetailView,
    StaffCreateView,
    StaffUpdateView,
    StaffDeleteView,
    LoginAPIView, 
    RegisterAPIView,
    RefreshTokenAPIView,
    LogoutAPIView,
    DashboardStatsAPIView,
    )


urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('token/refresh/', RefreshTokenAPIView.as_view(), name='token-refresh'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    
    path('staffs/', StaffListView.as_view(), name='staff-list'),
    path('staffs/<int:pk>/', StaffDetailView.as_view(), name='staff-detail'),
    path('staffs/create/', StaffCreateView.as_view(), name='staff-create'),
    path('staffs/<int:pk>/update/', StaffUpdateView.as_view(), name='staff-update'),
    path('staffs/<int:pk>/delete/', StaffDeleteView.as_view(), name='staff-delete'),
    path('staff/team/', StaffByTeamView.as_view(), name='staff-by-team'),
    path("stats/", DashboardStatsAPIView.as_view(), name="dashboard-stats"),
    path("activities/", RecentActivitiesAPIView.as_view(), name="dashboard-activities"),
]
