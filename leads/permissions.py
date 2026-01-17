from rest_framework.permissions import BasePermission

# Roles allowed to access leads fully
LEAD_ACCESS_ROLES = [
    "ADMIN",
    "OPS",
    "ADM_MANAGER",
    "ADM_EXEC",
    "PROCESSING",
    "MEDIA",
    "TRAINER",
    "BUSINESS_HEAD",
    "BDM",
    "CM",
    "HR",
    "FOE",
]

# Roles who can view ALL leads
LEAD_VIEW_ALL_ROLES = [
    "ADMIN",
    "BUSINESS_HEAD",
    "OPS",
    "HR",
    'MEDIA',
]

class CanAccessLeads(BasePermission):
    """
    Checks if user role is allowed to access leads
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in LEAD_ACCESS_ROLES
