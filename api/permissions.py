"""
Custom DRF permission classes for fine-grained access control.

Includes role-based access (e.g., staff, candidate, league-specific),
object-level access, and read-only constraints.
"""

from rest_framework.permissions import BasePermission


class IsDeveloper(BasePermission):
    """
    Grants access if the authenticated user has a related Candidate profile.
    """

    def has_permission(self, request, view):
        return hasattr(request.user, "developer")
