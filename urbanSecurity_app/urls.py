from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'access-logs', views.AccessLogViewSet)
router.register(r'audit-logs', views.AuditLogViewSet)
router.register(r'abac-policies', views.ABACPolicyViewSet)
router.register(r'role-adaptations', views.RoleAdaptationViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/adapt-role/', views.AdaptRoleView.as_view(), name='adapt-role'),
    path('api/anomaly-detect/', views.AnomalyDetectView.as_view(), name='anomaly-detect'),
    path('api/blockchain-verify/', views.BlockchainVerifyView.as_view(), name='blockchain-verify'),
    path('', views.api_root, name='api-root'),
]