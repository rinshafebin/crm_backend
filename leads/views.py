from rest_framework import generics, filters, status
from rest_framework.permissions import IsAdminUser
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

from .models import Lead, ProcessingUpdate
from .serializers import (
    LeadListSerializer,
    LeadDetailSerializer,
    LeadCreateSerializer,
    ProcessingUpdateSerializer
)



class LeadPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# ------------------------- Lead List View -------------------------
class LeadListView(generics.ListAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadListSerializer
    permission_classes = [IsAdminUser]
    pagination_class = LeadPagination

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]

    # Filtering options
    filterset_fields = [
        'priority',
        'status',
        'source',
        'processing_status',
        'assigned_to',
    ]

    # Searchable fields
    search_fields = ['name', 'phone', 'email', 'program']

    # Ordering options
    ordering_fields = ['created_at', 'priority']
    ordering = ['-created_at']


# ------------------------- Lead Create View -------------------------
class LeadCreateView(generics.CreateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadCreateSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        """Optionally customize the create response"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lead = serializer.save()
        return Response({
            "message": "Lead created successfully",
            "lead_id": lead.id
        }, status=status.HTTP_201_CREATED)



# ------------------------- Lead Detail View ------------------------- 
class LeadDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadDetailSerializer
    permission_classes = [IsAdminUser]

    def update(self, request, *args, **kwargs):
        """Customize update response"""
        response = super().update(request, *args, **kwargs)
        response.data = {"message": "Lead updated successfully"}
        return response

    def destroy(self, request, *args, **kwargs):
        """Customize delete response"""
        super().destroy(request, *args, **kwargs)
        return Response({"message": "Lead deleted successfully"}, status=status.HTTP_204_NO_CONTENT)



# ------------------------- Lead Processing Timeline View -------------------------
class LeadProcessingTimelineView(generics.ListAPIView):
    serializer_class = ProcessingUpdateSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        lead_id = self.kwargs.get('lead_id')
        return ProcessingUpdate.objects.filter(lead_id=lead_id).order_by('-timestamp')
