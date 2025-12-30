from rest_framework import serializers
from django.utils import timezone
from .models import Task, TaskUpdate

# -------------------------- Task Serializer -------------------------
class TaskSerializer(serializers.ModelSerializer):
    assigned_by_name = serializers.CharField(source='assigned_by.username', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)

    # Computed fields
    overdue_days = serializers.SerializerMethodField()
    days_until_deadline = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    # Make assigned_by read-only (set in view)
    assigned_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description',
            'assigned_by', 'assigned_by_name',
            'assigned_to', 'assigned_to_name',
            'status', 'priority', 'deadline',
            'created_at', 'updated_at', 'completed_at',
            'overdue_days', 'days_until_deadline', 'is_overdue'
        ]

    # ------------------ Computed field methods ------------------
    def get_overdue_days(self, obj):
        if obj.deadline and obj.status not in ['COMPLETED', 'CANCELLED']:
            delta = timezone.now().date() - obj.deadline
            return delta.days if delta.days > 0 else 0
        return 0

    def get_days_until_deadline(self, obj):
        if obj.deadline and obj.status not in ['COMPLETED', 'CANCELLED']:
            delta = obj.deadline - timezone.now().date()
            return delta.days if delta.days > 0 else 0
        return 0

    def get_is_overdue(self, obj):
        return obj.status not in ['COMPLETED', 'CANCELLED'] and obj.deadline and obj.deadline < timezone.now().date()

    # ------------------ Field validations ------------------
    def validate_deadline(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Deadline must be in the future.")
        return value

    def validate_assigned_to(self, value):
        if value.role not in ['MEDIA', 'ADM_MANAGER', 'ADM_EXEC']:
            raise serializers.ValidationError("Task must be assigned to MEDIA / ADM_MANAGER / ADM_EXEC users.")
        return value

    # ------------------ Cross-field validation ------------------
    def validate(self, attrs):
        request = self.context.get('request')

        # assigned_by ≠ assigned_to
        if request and 'assigned_to' in attrs:
            if request.user == attrs['assigned_to']:
                raise serializers.ValidationError("assigned_by and assigned_to cannot be the same user.")

        # Status transition validation
        if self.instance and 'status' in attrs:
            current = self.instance.status
            new = attrs['status']

            invalid = {
                'PENDING': ['COMPLETED'],
                'COMPLETED': ['PENDING', 'IN_PROGRESS'],
                'CANCELLED': ['PENDING', 'IN_PROGRESS'],
            }

            if new in invalid.get(current, []):
                raise serializers.ValidationError(f"Cannot change status from {current} to {new}.")

        return attrs


# ----------------------- Task Update Serializer -----------------------
class TaskUpdateSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(source='updated_by.username', read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)
    task = serializers.PrimaryKeyRelatedField(read_only=True)  # Set in view, not from client

    class Meta:
        model = TaskUpdate
        fields = [
            'id', 'task', 'updated_by', 'updated_by_name',
            'previous_status', 'new_status', 'notes', 'created_at'
        ]

    # ------------------ Validation ------------------
    def validate(self, attrs):
        task = attrs.get('task')
        new_status = attrs.get('new_status')
        notes = attrs.get('notes', '')

        # Ensure status actually changes
        if task and new_status == task.status:
            raise serializers.ValidationError("New status must be different from the current status.")

        # Optional: require notes for COMPLETED / CANCELLED
        if new_status in ['COMPLETED', 'CANCELLED'] and not notes:
            raise serializers.ValidationError("Notes are required when completing or cancelling a task.")

        return attrs
