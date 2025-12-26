from django.urls import path
from .views import (
    LeadListView,
    LeadCreateView,
    LeadDetailView,
    LeadProcessingTimelineView
)

urlpatterns = [
    path('leads/', LeadListView.as_view(), name='lead-list'),

    # Create a new lead
    path('leads/create/', LeadCreateView.as_view(), name='lead-create'),

    # Retrieve, update, or delete a specific lead
    path('leads/<int:pk>/', LeadDetailView.as_view(), name='lead-detail'),

    # Get the processing timeline for a specific lead
    path('leads/<int:lead_id>/timeline/', LeadProcessingTimelineView.as_view(), name='lead-processing-timeline'),
]
