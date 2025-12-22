# leads/urls.py
from django.urls import path
from .views import AdminLeadListView

urlpatterns = [
    path('admin/leads/', AdminLeadListView.as_view()),
]
