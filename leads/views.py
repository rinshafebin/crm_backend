from rest_framework import generics, filters, status
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from leads.permissions import CanAccessLeads,LEAD_VIEW_ALL_ROLES
from .models import Lead, ProcessingUpdate, RemarkHistory
from .serializers import (
    LeadListSerializer,
    LeadDetailSerializer,
    LeadCreateSerializer,
    ProcessingUpdateSerializer,
    LeadUpdateSerializer
)


#  Pagination 
class LeadPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

#  Lead List View 
class LeadListView(generics.ListAPIView):
    serializer_class = LeadListSerializer
    permission_classes = [CanAccessLeads]  
    pagination_class = LeadPagination

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = ['priority', 'status', 'source', 'processing_status', 'assigned_to']
    search_fields = ['name', 'phone', 'email', 'program']
    ordering_fields = ['created_at', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        # Admins and business heads can see all leads
        if user.role in ["ADMIN", "BUSINESS_HEAD", "OPS", "HR"]:
            return Lead.objects.all().distinct()
        # Other roles see only leads assigned to them
        return Lead.objects.filter(assigned_to=user).distinct()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Pagination
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        # Stats for the user
        stats = {
            "new": queryset.filter(status__iexact='ENQUIRY').count(),
            "qualified": queryset.filter(status__iexact='QUALIFIED').count(),
            "converted": queryset.filter(status__iexact='CONVERTED').count(),
        }

        return self.get_paginated_response({
            "leads": serializer.data,
            "stats": stats,
        })


#  Lead Create View 
class LeadCreateView(generics.CreateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadCreateSerializer
    permission_classes = [CanAccessLeads] 

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lead = serializer.save()

        if getattr(lead, 'processing_status', None) and lead.processing_status != 'PENDING':
            ProcessingUpdate.objects.create(
                lead=lead,
                status=lead.processing_status,
                changed_by=request.user,
                notes="Initial status on lead creation"
            )

        return Response({
            "message": "Lead created successfully",
            "lead_id": lead.id
        }, status=status.HTTP_201_CREATED)



#  Lead Detail View 
class LeadDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadDetailSerializer
    permission_classes = [CanAccessLeads]

    def get_queryset(self):
        user = self.request.user
        if user.role in ["ADMIN", "BUSINESS_HEAD", "OPS", "HR"]:
            return Lead.objects.all()
        return Lead.objects.filter(assigned_to=user)

    def update(self, request, *args, **kwargs):
        lead = self.get_object()
        old_processing_status = lead.processing_status
        old_remarks = lead.remarks

        response = super().update(request, *args, **kwargs)
        updated_lead = self.get_object()

        if old_remarks != updated_lead.remarks:
            RemarkHistory.objects.create(
                lead=updated_lead,
                previous_remarks=old_remarks,
                new_remarks=updated_lead.remarks,
                changed_by=request.user
            )

        if old_processing_status != updated_lead.processing_status:
            ProcessingUpdate.objects.create(
                lead=updated_lead,
                status=updated_lead.processing_status,
                changed_by=request.user,
                notes="Status updated via API"
            )

        response.data = {"message": "Lead updated successfully"}
        return response

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"message": "Lead deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


#  Lead Processing Timeline View 
class LeadProcessingTimelineView(generics.ListAPIView):
    serializer_class = ProcessingUpdateSerializer
    permission_classes = [CanAccessLeads]

    def get_queryset(self):
        lead_id = self.kwargs.get('lead_id')
        lead = get_object_or_404(Lead, id=lead_id)
        user = self.request.user
        if lead.assigned_to != user and user.role not in LEAD_VIEW_ALL_ROLES:
            return Lead.objects.none()
        return ProcessingUpdate.objects.filter(lead=lead).order_by('-timestamp')



class UpdateLeadView(APIView):
    permission_classes = [CanAccessLeads]

    def patch(self, request, lead_id):
        lead = get_object_or_404(Lead, id=lead_id)

        if lead.assigned_to != request.user and request.user.role not in LEAD_VIEW_ALL_ROLES:
            return Response({"error": "Permission denied"}, status=403)

        serializer = LeadUpdateSerializer(
            lead,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=200)
