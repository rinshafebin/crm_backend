from rest_framework import serializers
from .models import Task, TaskUpdate
from accounts.models import User

class TaskSerializer(serializers.ModelSerializer):
    assigned_by_name = serializers.CharField(source='assigned_by.username', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    
    overdue_days = serializers.ReadOnlyField()
    days_until_deadline = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    assigned_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'assigned_by',
            'assigned_by_name',
            'assigned_to',
            'assigned_to_name',
            'status',
            'priority',
            'deadline',
            'created_at',
            'updated_at',
            'completed_at',
            'overdue_days',
            'days_until_deadline',
            'is_overdue',
        ]


class TaskUpdateSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(source='updated_by.username', read_only=True)

    # updated_by is read-only because it's automatically set to request.user in the view
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = TaskUpdate
        fields = [
            'id',
            'task',
            'updated_by',
            'updated_by_name',
            'previous_status',
            'new_status',
            'notes',
            'created_at',
        ]
