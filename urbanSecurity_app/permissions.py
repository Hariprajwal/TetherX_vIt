# urbanSecurity_app/permissions.py
"""
Role-Based Access Control (RBAC) permissions for UrbanSecure.

Roles hierarchy (highest → lowest):
  admin      → Full access to everything
  Municipal  → Read/Write on all data, cannot delete policies
  Engineer   → Read access logs, use AI tools, cannot manage policies
  viewer     → Read-only access to own logs only
"""
from rest_framework.permissions import BasePermission

# Helper to extract role from user
def get_user_role(request):
    if not request.user or not request.user.is_authenticated:
        return 'anonymous'
    # Superusers are always admin
    if request.user.is_superuser:
        return 'admin'
    return (request.user.first_name or 'viewer').lower()


ROLE_HIERARCHY = {'admin': 4, 'municipal': 3, 'engineer': 2, 'viewer': 1, 'anonymous': 0}

def role_level(role):
    return ROLE_HIERARCHY.get(role.lower(), 0)


class IsAdmin(BasePermission):
    """Only admin users."""
    message = "Admin access required."
    def has_permission(self, request, view):
        return get_user_role(request) == 'admin'


class IsAdminOrMunicipal(BasePermission):
    """Admin or Municipal role."""
    message = "Municipal or Admin access required."
    def has_permission(self, request, view):
        return role_level(get_user_role(request)) >= 3


class IsAtLeastEngineer(BasePermission):
    """Admin, Municipal, or Engineer role."""
    message = "Engineer, Municipal, or Admin access required."
    def has_permission(self, request, view):
        return role_level(get_user_role(request)) >= 2


class IsAuthenticated(BasePermission):
    """Any authenticated user."""
    message = "Authentication required."
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


# ──────────────────────────────────────────────
# Composite permissions for specific resources
# ──────────────────────────────────────────────

class AccessLogPermission(BasePermission):
    """
    - admin/Municipal: Full CRUD on all logs
    - Engineer: Read all, Create own, no Delete
    - viewer: Read own logs only
    """
    message = "You do not have permission for this action on Access Logs."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = get_user_role(request)
        if role in ('admin', 'municipal'):
            return True
        if role == 'engineer':
            return request.method in ('GET', 'HEAD', 'OPTIONS', 'POST')
        if role == 'viewer':
            return request.method in ('GET', 'HEAD', 'OPTIONS')
        return False


class AuditLogPermission(BasePermission):
    """
    - admin/Municipal: Full CRUD
    - Engineer: Read + Create
    - viewer: Read only
    """
    message = "You do not have permission for this action on Audit Logs."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = get_user_role(request)
        if role in ('admin', 'municipal'):
            return True
        if role == 'engineer':
            return request.method in ('GET', 'HEAD', 'OPTIONS', 'POST')
        if role == 'viewer':
            return request.method in ('GET', 'HEAD', 'OPTIONS')
        return False


class ABACPolicyPermission(BasePermission):
    """
    - admin: Full CRUD (create, edit, delete policies)
    - Municipal: Read + Create (cannot delete)
    - Engineer/viewer: Read only
    """
    message = "You do not have permission to manage ABAC Policies."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = get_user_role(request)
        if role == 'admin':
            return True
        if role == 'municipal':
            return request.method in ('GET', 'HEAD', 'OPTIONS', 'POST', 'PUT', 'PATCH')
        # Engineer + viewer: read only
        return request.method in ('GET', 'HEAD', 'OPTIONS')


class RoleAdaptationPermission(BasePermission):
    """
    - admin/Municipal: Full access
    - Engineer: Read only
    - viewer: Read own only
    """
    message = "You do not have permission for Role Adaptations."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = get_user_role(request)
        if role in ('admin', 'municipal'):
            return True
        return request.method in ('GET', 'HEAD', 'OPTIONS')


class AIToolPermission(BasePermission):
    """
    - admin/Municipal/Engineer: Can use AI tools
    - viewer: Cannot use AI tools (read info only)
    """
    message = "Engineer, Municipal, or Admin access required for AI tools."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = get_user_role(request)
        if role in ('admin', 'municipal', 'engineer'):
            return True
        # viewer can only GET (see info)
        return request.method in ('GET', 'HEAD', 'OPTIONS')
