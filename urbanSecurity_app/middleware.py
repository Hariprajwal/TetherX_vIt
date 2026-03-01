# urbanSecurity_app/middleware.py
# ABAC Zero-Trust Middleware — evaluates attribute-based policies on every request.
# Skips admin, static, and API schema paths. Logs access via AccessLog model.

import logging
from datetime import datetime
from django.http import HttpResponseForbidden

logger = logging.getLogger(__name__)

# Paths that bypass ABAC checks
EXEMPT_PATHS = ['/admin/', '/static/', '/favicon.ico']


class ABACZeroTrustMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip ABAC for exempt paths
        if any(request.path.startswith(p) for p in EXEMPT_PATHS):
            return self.get_response(request)

        # Extract attributes for zero-trust evaluation
        ip = self._get_client_ip(request)
        current_hour = datetime.now().hour
        role = getattr(request.user, 'role', None) or request.META.get('HTTP_X_USER_ROLE', 'viewer')
        method = request.method

        # ABAC Policy Check: example rules
        if not self._check_abac_policies(role, current_hour, ip, method, request.path):
            logger.warning(
                f"ABAC DENIED: role={role}, ip={ip}, hour={current_hour}, "
                f"method={method}, path={request.path}"
            )
            return HttpResponseForbidden(
                "Access denied by ABAC Zero-Trust policy. "
                "Your attributes do not satisfy the required conditions."
            )

        # Log access (non-blocking, best-effort)
        try:
            from .models import AccessLog
            AccessLog.objects.create(
                user_identifier=str(getattr(request.user, 'username', 'anonymous')),
                endpoint=request.path,
                method=method,
                role=role,
                ip_address=ip,
            )
        except Exception as e:
            logger.debug(f"Access log skipped (likely during migrations): {e}")

        return self.get_response(request)

    def _get_client_ip(self, request):
        """Extract client IP from X-Forwarded-For or REMOTE_ADDR."""
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            return xff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '127.0.0.1')

    def _check_abac_policies(self, role, current_hour, ip, method, path):
        """
        Evaluate ABAC policies. Returns True if access is allowed.
        Rules are evaluated from DB if available, else uses defaults.
        """
        try:
            from .models import ABACPolicy
            policies = ABACPolicy.objects.filter(is_active=True, role=role)
            for policy in policies:
                if not self._evaluate_condition(policy, current_hour, ip, method, path):
                    return False
        except Exception:
            # During migrations or if table doesn't exist yet, use default rules
            pass

        # Default rules (always applied)
        # Rule: Engineers cannot access after 8 PM (hour >= 20)
        if role == 'Engineer' and current_hour >= 20:
            return False

        # Rule: Deny DELETE for non-Municipal roles
        if method == 'DELETE' and role not in ('Municipal', 'admin'):
            return False

        return True

    def _evaluate_condition(self, policy, current_hour, ip, method, path):
        """Evaluate a single ABAC policy condition. Returns True if allowed."""
        try:
            condition = policy.condition.lower()
            if 'hour' in policy.attribute.lower():
                # e.g. condition = ">= 20" with action = "deny"
                if policy.action == 'deny':
                    # If condition matches, deny
                    if eval(f"{current_hour} {condition}"):
                        return False
            return True
        except Exception:
            return True  # Fail-open for malformed policies (log in production)