from django.urls import path
from .views import (
    StaffListView,
    StaffDetailView,
    StaffCreateView,
    StaffUpdateView,
    StaffDeleteView,
    LoginAPIView, 
    RegisterAPIView
)


urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('staffs/', StaffListView.as_view(), name='staff-list'),
    path('staffs/<int:pk>/', StaffDetailView.as_view(), name='staff-detail'),
    path('staffs/create/', StaffCreateView.as_view(), name='staff-create'),
    path('staffs/<int:pk>/update/', StaffUpdateView.as_view(), name='staff-update'),
    path('staffs/<int:pk>/delete/', StaffDeleteView.as_view(), name='staff-delete'),
    
]
