# leads/urls.py
from django.urls import path
from .views import AdminLeadListView,LeadCreateView

urlpatterns = [
    path('admin/leads/', AdminLeadListView.as_view()),
    path('leads/create/', LeadCreateView.as_view(), name='lead-create'),

]
