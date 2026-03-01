from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from .auth_views import (
    RegisterView, CurrentUserView,
    PasswordChangeView, AccountDeleteView,
    CheckUsernameView, CheckEmailView,
)

router = DefaultRouter()
router.register(r'access-logs', views.AccessLogViewSet, basename='accesslog')
router.register(r'audit-logs', views.AuditLogViewSet, basename='auditlog')
router.register(r'abac-policies', views.ABACPolicyViewSet, basename='abacpolicy')
router.register(r'role-adaptations', views.RoleAdaptationViewSet, basename='roleadaptation')

urlpatterns = [
    # Auth endpoints
    path('api/auth/register/', RegisterView.as_view(), name='auth-register'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='auth-login'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('api/auth/me/', CurrentUserView.as_view(), name='auth-me'),
    path('api/auth/change-password/', PasswordChangeView.as_view(), name='auth-change-password'),
    path('api/auth/delete-account/', AccountDeleteView.as_view(), name='auth-delete-account'),
    path('api/auth/check-username/', CheckUsernameView.as_view(), name='auth-check-username'),
    path('api/auth/check-email/', CheckEmailView.as_view(), name='auth-check-email'),

    # CRUD endpoints
    path('api/', include(router.urls)),

    # AI / Action endpoints
    path('api/adapt-role/', views.AdaptRoleView.as_view(), name='adapt-role'),
    path('api/anomaly-detect/', views.AnomalyDetectView.as_view(), name='anomaly-detect'),
    path('api/blockchain-verify/', views.BlockchainVerifyView.as_view(), name='blockchain-verify'),

    # API root
    path('', views.api_root, name='api-root'),
]