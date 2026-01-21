from django.urls import path
from .views import (
    LeadListView,
    LeadCreateView,
    LeadDetailView,
    LeadProcessingTimelineView,
)

app_name = 'leads'

urlpatterns = [
    # List all leads (with filtering, search, pagination)
    path('leads/', LeadListView.as_view(), name='lead-list'),
    path('leads/create/', LeadCreateView.as_view(), name='lead-create'),
    # Retrieve, update, or delete a specific lead
    path('leads/<int:pk>/', LeadDetailView.as_view(), name='lead-detail'),
    path('leads/<int:lead_id>/timeline/', LeadProcessingTimelineView.as_view(), name='lead-timeline'),
]