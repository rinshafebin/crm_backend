from rest_framework.permissions import BasePermission

# Roles who can review reports
REPORT_REVIEWERS = [
    "ADMIN",
    "BUSINESS_HEAD",
    "OPS",
    "GENERAL_MANAGER",
    "HR",
]

class IsReportReviewer(BasePermission):
    """
    Can view all reports & approve/reject
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in REPORT_REVIEWERS
        )


class IsReportOwner(BasePermission):
    """
    Object-level: only owner
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
