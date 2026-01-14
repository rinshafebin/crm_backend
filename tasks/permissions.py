from rest_framework.permissions import BasePermission

TOP_MANAGEMENT = [
    "ADMIN",
    "BUSINESS_HEAD",
]

OPERATIONS = [
    "OPS",
    "GENERAL_MANAGER",
    "CM",
    "BDM",
]

HR_ROLES = [
    "HR",
]

EXECUTION_ROLES = [
    "MEDIA",
    "ADM_EXEC",
    "ADM_MANAGER",
    "PROCESSING",
    "FOE",
    "TRAINER",
]

TASK_ASSIGNERS = TOP_MANAGEMENT + OPERATIONS + HR_ROLES
TASK_ASSIGNEES = EXECUTION_ROLES


class IsTaskAssigner(BasePermission):
    """
    Can create, update, delete tasks
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in TASK_ASSIGNERS
        )


class IsTaskAssignee(BasePermission):
    """
    Can receive tasks and update status
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in TASK_ASSIGNEES
        )


class IsAssigneeOfTask(BasePermission):
    """
    Object-level: only assigned employee
    """
    def has_object_permission(self, request, view, obj):
        return obj.assigned_to == request.user
