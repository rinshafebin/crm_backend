from rest_framework.permissions import BasePermission

class CanCreateLead(BasePermission):
    """
    Allow only users who are ADMIN, ADM_MANAGER, or ADM_EXEC to create leads
    """
    allowed_roles = ['ADMIN', 'ADM_MANAGER', 'ADM_EXEC']

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in self.allowed_roles
        )
