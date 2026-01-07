from django.urls import path
from .views import (
    LeadListView,
    LeadCreateView,
    LeadDetailView,
    LeadProcessingTimelineView,
    UpdateLeadPriorityView,
    UpdateLeadStatusView,
    UpdateLeadProgramView
)

urlpatterns = [
    path('leads/', LeadListView.as_view(), name='lead-list'),
    path('leads/create/', LeadCreateView.as_view(), name='lead-create'),
    path('leads/<int:pk>/', LeadDetailView.as_view(), name='lead-detail'),

    # Processing timeline
    path('leads/<int:lead_id>/timeline/', LeadProcessingTimelineView.as_view(), name='lead-timeline'),

    # Individual field updates
    path('leads/<int:lead_id>/update-priority/', UpdateLeadPriorityView.as_view(), name='update-priority'),
    path('leads/<int:lead_id>/update-status/', UpdateLeadStatusView.as_view(), name='update-status'),
    path('leads/<int:lead_id>/update-program/', UpdateLeadProgramView.as_view(), name='update-program'),
]
