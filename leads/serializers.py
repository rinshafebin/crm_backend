from rest_framework import serializers
from .models import Lead, ProcessingUpdate, RemarkHistory


# --------------------------- Lead Create Serializer ---------------------------
class LeadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = [
            'name',
            'phone',
            'email',
            'source',
            'custom_source',
            'priority',
            'program',
            'location',
            'remarks',
            'status',
        ]

    # Field-level validations
    def validate_name(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters long.")
        return value

    def validate_phone(self, value):
        value = value.strip()
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        if len(value) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits.")
        
        # Prevent duplicate phone
        if Lead.objects.filter(phone=value).exists():
            raise serializers.ValidationError("A lead with this phone number already exists.")
        return value

    def validate_email(self, value):
        if value:
            value = value.strip()
            if Lead.objects.filter(email=value).exists():
                raise serializers.ValidationError("A lead with this email already exists.")
        return value

    # Object-level validation
    def validate(self, attrs):
        source = attrs.get('source')
        custom_source = attrs.get('custom_source')

        # Require custom_source if source is OTHER
        if source == 'OTHER' and not custom_source:
            raise serializers.ValidationError({"custom_source": "This field is required when source is OTHER."})

        # Restrict invalid initial status
        if attrs.get('status') in ['REGISTERED', 'COMPLETED']:
            raise serializers.ValidationError({"status": "Cannot create a lead directly with this status."})

        return attrs


# --------------------------- Lead List Serializer ---------------------------
class LeadListSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)

    class Meta:
        model = Lead
        fields = [
            'id',
            'name',
            'phone',
            'status',
            'priority',
            'program',
            'source',
            'processing_status',
            'assigned_to_name',
            'created_at',
        ]


# --------------------------- Lead Detail Serializer ---------------------------
class LeadDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'
        read_only_fields = (
            'created_at',
            'updated_at',
            'processing_status_date',
            'registration_date',
        )

    def update(self, instance, validated_data):
        request = self.context.get('request')

        # Track remarks changes
        if 'remarks' in validated_data and instance.remarks != validated_data.get('remarks'):
            RemarkHistory.objects.create(
                lead=instance,
                previous_remarks=instance.remarks,
                new_remarks=validated_data.get('remarks'),
                changed_by=request.user if request else None
            )

        return super().update(instance, validated_data)


# --------------------------- Processing Update Serializer ---------------------------
class ProcessingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessingUpdate
        fields = [
            'id',
            'lead',
            'status',
            'changed_by',
            'notes',
            'timestamp',
        ]
        read_only_fields = ('timestamp',)

    def validate_status(self, value):
        if value not in dict(Lead.PROCESSING_STATUS_CHOICES).keys():
            raise serializers.ValidationError("Invalid processing status.")
        return value

    def validate(self, attrs):
        lead = attrs.get('lead')
        changed_by = attrs.get('changed_by')

        if not Lead.objects.filter(id=lead.id).exists():
            raise serializers.ValidationError({"lead": "Lead does not exist."})

        if changed_by and changed_by.role != 'PROCESSING':
            raise serializers.ValidationError({"changed_by": "User must have PROCESSING role to update status."})

        return attrs


# --------------------------- Remark History Serializer ---------------------------
class RemarkHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RemarkHistory
        fields = [
            'id',
            'lead',
            'previous_remarks',
            'new_remarks',
            'changed_by',
            'changed_at',
        ]
        read_only_fields = ('changed_at',)

    def validate_changed_by(self, value):
        if not value:
            raise serializers.ValidationError("Changed by must be provided.")
        return value
