from rest_framework.generics import ListAPIView
from .models import Lead
from .serializers import AdminLeadListSerializer
from users.permissions import IsAdmin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LeadCreateSerializer
from .permissions import CanCreateLead

class AdminLeadListView(ListAPIView):
    queryset = Lead.objects.select_related('assigned_to').all()
    serializer_class = AdminLeadListSerializer
    permission_classes = [IsAdmin]

class LeadCreateView(APIView):
    permission_classes = [CanCreateLead]

    def post(self, request):
        serializer = LeadCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
