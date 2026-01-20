from rest_framework.permissions import BasePermission


class IsManagement(BasePermission):
    """
    Management-level users who can view staff lists and details
    """
    allowed_roles = [
        "ADMIN",
        "OPS",
        "BUSINESS_HEAD",
        "HR",
        "ADM_MANAGER",
        "CM",
        "BDM",
        'HR'
    ]

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in self.allowed_roles
        )


class IsSuperAdmin(BasePermission):
    """
    Very restricted actions like deleting staff
    """
    allowed_roles = [
        "ADMIN",
        "BUSINESS_HEAD",
    ]

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in self.allowed_roles
        )
