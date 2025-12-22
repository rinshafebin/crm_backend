from rest_framework import serializers
from .models import Lead

class AdminLeadListSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(
        source='assigned_to.username',  
        read_only=True
    )

    class Meta:
        model = Lead
        fields = [
            'name',
            'phone',
            'source',
            'status',
            'program',
            'assigned_to_name',
            'created_at',
        ]



class LeadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__' 
        read_only_fields = ['created_at', 'updated_at', 'processing_status_date', 'registration_date']
