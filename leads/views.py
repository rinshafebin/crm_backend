from rest_framework.generics import ListAPIView
from .models import Lead
from .serializers import AdminLeadListSerializer
from users.permissions import IsAdmin

class AdminLeadListView(ListAPIView):
    queryset = Lead.objects.select_related('assigned_to').all()
    serializer_class = AdminLeadListSerializer
    permission_classes = [IsAdmin]
