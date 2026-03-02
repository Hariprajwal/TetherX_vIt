# urbanSecurity_app/permissions.py
"""
Role-Based Access Control (RBAC) permissions for UrbanSecure.

Roles hierarchy (highest → lowest):
  admin      → Django superuser only (not registerable)
  Municipal  → Read/Write on all data, cannot delete policies
  Engineer   → Read access logs, use AI tools, cannot manage policies
  viewer     → Read-only access to own logs only
"""
from rest_framework.permissions import BasePermission


def get_user_role(request):
    """Extract effective role from the custom User model."""
    if not request.user or not request.user.is_authenticated:
        return 'anonymous'
    return request.user.get_effective_role()


ROLE_HIERARCHY = {'admin': 4, 'municipal': 3, 'engineer': 2, 'viewer': 1, 'anonymous': 0}

def role_level(role):
    return ROLE_HIERARCHY.get(role.lower(), 0)


class IsAdmin(BasePermission):
    message = "Admin access required."
    def has_permission(self, request, view):
        return get_user_role(request) == 'admin'


class IsAdminOrMunicipal(BasePermission):
    message = "Municipal or Admin access required."
    def has_permission(self, request, view):
        return role_level(get_user_role(request)) >= 3


class IsAtLeastEngineer(BasePermission):
    message = "Engineer, Municipal, or Admin access required."
    def has_permission(self, request, view):
        return role_level(get_user_role(request)) >= 2


class AccessLogPermission(BasePermission):
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
    message = "You do not have permission to manage ABAC Policies."
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = get_user_role(request)
        if role == 'admin':
            return True
        if role == 'municipal':
            return request.method in ('GET', 'HEAD', 'OPTIONS', 'POST', 'PUT', 'PATCH')
        return request.method in ('GET', 'HEAD', 'OPTIONS')


class RoleAdaptationPermission(BasePermission):
    message = "You do not have permission for Role Adaptations."
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = get_user_role(request)
        if role in ('admin', 'municipal'):
            return True
        return request.method in ('GET', 'HEAD', 'OPTIONS')


class AIToolPermission(BasePermission):
    message = "Engineer, Municipal, or Admin access required for AI tools."
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = get_user_role(request)
        if role in ('admin', 'municipal', 'engineer'):
            return True
        return request.method in ('GET', 'HEAD', 'OPTIONS')
