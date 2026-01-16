from django.urls import path
from .views import (
    LeadListView,
    LeadCreateView,
    LeadDetailView,
    LeadProcessingTimelineView,
    UpdateLeadView, 
)

urlpatterns = [
    path('leads/', LeadListView.as_view(), name='lead-list'),
    path('leads/create/', LeadCreateView.as_view(), name='lead-create'),
    path('leads/<int:pk>/', LeadDetailView.as_view(), name='lead-detail'),

    # Processing timeline
    path('leads/<int:lead_id>/timeline/', LeadProcessingTimelineView.as_view(), name='lead-timeline'),
    path('leads/<int:pk>/update/', UpdateLeadView.as_view(), name='lead-update'),
    
]
