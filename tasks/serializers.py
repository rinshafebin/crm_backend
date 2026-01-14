from rest_framework import serializers
from django.utils import timezone
from .models import Task, TaskUpdate
from django.contrib.auth import get_user_model

User = get_user_model()

#  Employee Serializer
class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role']


#  Task Serializer 
class TaskSerializer(serializers.ModelSerializer):
    assigned_by_name = serializers.CharField(source='assigned_by.username', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    assigned_by = serializers.PrimaryKeyRelatedField(read_only=True)
    overdue_days = serializers.SerializerMethodField()
    days_until_deadline = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

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

    #  Computed fields 
    def get_overdue_days(self, obj):
        if obj.deadline and obj.status not in ['COMPLETED', 'CANCELLED']:
            delta = timezone.now().date() - obj.deadline
            return max(delta.days, 0)
        return 0

    def get_days_until_deadline(self, obj):
        if obj.deadline and obj.status not in ['COMPLETED', 'CANCELLED']:
            delta = obj.deadline - timezone.now().date()
            return max(delta.days, 0)
        return 0

    def get_is_overdue(self, obj):
        return obj.status not in ['COMPLETED', 'CANCELLED'] and obj.deadline and obj.deadline < timezone.now().date()

    #  Field validation 
    def validate_deadline(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("Deadline cannot be in the past.")
        return value

    def validate_assigned_to(self, value):
        if not value:
            raise serializers.ValidationError("Assigned user is required.")
        if value.role not in [
            'MEDIA', 'ADM_MANAGER', 'ADM_EXEC',
            'TRAINER', 'BDM', 'FOE_CUM_TC'
        ]:
            raise serializers.ValidationError("You cannot assign tasks to this role.")
        return value

    #  Cross-field validation 
    def validate(self, attrs):
        request = self.context.get('request')
        assigned_to = attrs.get('assigned_to')
        # Prevent assigning task to yourself
        if request and assigned_to and request.user == assigned_to:
            raise serializers.ValidationError("You cannot assign a task to yourself.")
        return attrs


#  Task Update Serializer 
class TaskUpdateSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(source='updated_by.username', read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)
    task = serializers.PrimaryKeyRelatedField(read_only=True)  # Set in view context

    class Meta:
        model = TaskUpdate
        fields = [
            'id', 'task', 'updated_by', 'updated_by_name',
            'previous_status', 'new_status', 'notes', 'created_at'
        ]

    #  Validation 
    def validate(self, attrs):
        task = self.context.get('task')  
        if not task:
            raise serializers.ValidationError("Task context is required for validation.")

        new_status = attrs.get('new_status')
        notes = attrs.get('notes', '')

        # Ensure status actually changes
        if new_status == task.status:
            raise serializers.ValidationError("New status must be different from the current status.")

        # Require notes for COMPLETED / CANCELLED
        if new_status in ['COMPLETED', 'CANCELLED'] and not notes.strip():
            raise serializers.ValidationError("Notes are required when completing or cancelling a task.")

        return attrs


#  Upcoming Task Serializer
class UpcomingTaskSerializer(serializers.ModelSerializer):
    priority_label = serializers.CharField(source="get_priority_display", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    days_left = serializers.IntegerField(source="days_until_deadline", read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "priority",
            "priority_label",
            "status",
            "status_label",
            "deadline",
            "days_left",
            "is_overdue",
        ]