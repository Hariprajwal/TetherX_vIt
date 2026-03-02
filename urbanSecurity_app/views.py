# urbanSecurity_app/views.py
import requests
import logging
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes as perm_decorator
from rest_framework.permissions import AllowAny

from .models import AccessLog, AuditLog, ABACPolicy, RoleAdaptation
from .serializers import (
    AccessLogSerializer, AuditLogSerializer,
    ABACPolicySerializer, RoleAdaptationSerializer,
    AdaptRoleRequestSerializer, AnomalyDetectRequestSerializer,
)
from .blockchain import LocalBlockchain
from .permissions import (
    get_user_role,
    AccessLogPermission, AuditLogPermission,
    ABACPolicyPermission, RoleAdaptationPermission,
    AIToolPermission,
)

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# CRUD ViewSets with Role-Based Permissions
# Data is segregated per-user via owner FK
# ──────────────────────────────────────────────

class AccessLogViewSet(viewsets.ModelViewSet):
    """
    Access Logs — per-user data segregation.
    - admin: see ALL logs from ALL users
    - Municipal: see ALL logs
    - Engineer: see ALL logs, can create, cannot delete
    - viewer: see only OWN logs
    """
    serializer_class = AccessLogSerializer
    permission_classes = [AccessLogPermission]

    def get_queryset(self):
        role = get_user_role(self.request)
        if role in ('admin', 'municipal', 'engineer'):
            return AccessLog.objects.all().order_by('-timestamp')
        # viewer: only their own logs (via owner FK)
        return AccessLog.objects.filter(
            owner=self.request.user
        ).order_by('-timestamp')

    def perform_create(self, serializer):
        """Auto-assign owner to the current user."""
        serializer.save(owner=self.request.user)


class AuditLogViewSet(viewsets.ModelViewSet):
    """
    Audit Logs — blockchain-integrated, per-user segregation.
    - admin/Municipal: see ALL, full CRUD
    - Engineer: see ALL, read + create
    - viewer: see only OWN
    """
    serializer_class = AuditLogSerializer
    permission_classes = [AuditLogPermission]

    def get_queryset(self):
        role = get_user_role(self.request)
        if role in ('admin', 'municipal', 'engineer'):
            return AuditLog.objects.all().order_by('-timestamp')
        return AuditLog.objects.filter(
            owner=self.request.user
        ).order_by('-timestamp')

    def perform_create(self, serializer):
        """Auto-generate blockchain hash on create + assign owner."""
        action = serializer.validated_data.get('action', '')
        actor = serializer.validated_data.get('actor', 'system')
        details = serializer.validated_data.get('details', '')
        data_str = f"{action}|{actor}|{details}"
        block = LocalBlockchain.add_block(data_str)
        serializer.save(
            owner=self.request.user,
            block_hash=block['hash'],
            prev_hash=block['prev_hash'],
            block_index=block['index'],
            verified=True,
        )


class ABACPolicyViewSet(viewsets.ModelViewSet):
    """
    ABAC Zero-Trust policies.
    - admin: FULL (create, edit, delete)
    - Municipal: read + create + edit (no delete)
    - Engineer/viewer: READ ONLY
    """
    queryset = ABACPolicy.objects.all().order_by('-priority')
    serializer_class = ABACPolicySerializer
    permission_classes = [ABACPolicyPermission]


class RoleAdaptationViewSet(viewsets.ModelViewSet):
    """
    Role Adaptations — per-user segregation.
    - admin/Municipal: see ALL
    - Engineer: see ALL (read only)
    - viewer: see OWN only
    """
    serializer_class = RoleAdaptationSerializer
    permission_classes = [RoleAdaptationPermission]

    def get_queryset(self):
        role = get_user_role(self.request)
        if role in ('admin', 'municipal', 'engineer'):
            return RoleAdaptation.objects.all().order_by('-timestamp')
        return RoleAdaptation.objects.filter(
            owner=self.request.user
        ).order_by('-timestamp')


# ──────────────────────────────────────────────
# AI Endpoints
# ──────────────────────────────────────────────

class AdaptRoleView(APIView):
    serializer_class = AdaptRoleRequestSerializer
    permission_classes = [AIToolPermission]

    def get(self, request):
        return Response({
            "info": "POST a context vector to get AI-recommended role",
            "example_body": {
                "context": [0.8, 0.3, 1.0, 0.5, 0.2],
                "user_identifier": "engineer_01",
                "current_role": "viewer"
            },
            "context_features": [
                "threat_level (0-1)",
                "time_of_day_normalized (0-1)",
                "location_risk (0-1)",
                "access_frequency (0-1)",
                "credential_strength (0-1)"
            ],
            "your_role": get_user_role(request),
        })

    def post(self, request):
        serializer = AdaptRoleRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        context = serializer.validated_data['context']
        user_id = serializer.validated_data.get('user_identifier', request.user.username)
        current_role = serializer.validated_data.get('current_role', get_user_role(request))

        recommended_role = None
        from_edge = False

        try:
            edge_url = "http://localhost:5001/edge-predict"
            resp = requests.post(edge_url, json={"context": context}, timeout=2)
            resp.raise_for_status()
            edge_data = resp.json()
            recommended_role = edge_data.get("recommended_role")
            from_edge = True
            edge_status = edge_data.get("status")
        except Exception:
            try:
                from .utils.RoleLSTM import RolePredictor
                recommended_role = RolePredictor.predict(context)
                from_edge = False
                edge_status = "edge_unavailable_local_fallback"
            except Exception as e:
                logger.error(f"Both edge and local prediction failed: {e}")
                recommended_role = "normal"
                edge_status = f"fallback_default: {str(e)}"

        RoleAdaptation.objects.create(
            owner=request.user,
            user_identifier=user_id,
            old_role=current_role,
            new_role=recommended_role,
            context_vector=context,
            reason=edge_status,
            adapted_by='edge' if from_edge else 'local',
            from_edge=from_edge,
        )

        LocalBlockchain.add_block(
            f"role_adapt|{user_id}|{current_role}→{recommended_role}"
        )

        return Response({
            "recommended_role": recommended_role,
            "from_edge": from_edge,
            "edge_status": edge_status,
            "user_identifier": user_id,
            "previous_role": current_role,
        }, status=status.HTTP_200_OK)


class AnomalyDetectView(APIView):
    serializer_class = AnomalyDetectRequestSerializer
    permission_classes = [AIToolPermission]

    def get(self, request):
        return Response({
            "info": "POST an input_vector to detect anomalies",
            "example_body": {
                "input_vector": [0.8, 0.3, 1.0, 0.5, 0.2],
                "user_identifier": "sensor_42"
            },
            "your_role": get_user_role(request),
        })

    def post(self, request):
        serializer = AnomalyDetectRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        input_vector = serializer.validated_data['input_vector']
        user_id = serializer.validated_data.get('user_identifier', request.user.username)

        try:
            from .utils.RoleLSTM import AnomalyDetector
            detector = AnomalyDetector()
            is_anomalous = detector.detect(input_vector)
            anomaly_score = 0.85 if is_anomalous else 0.05
        except Exception as e:
            logger.warning(f"Anomaly detection model unavailable: {e}")
            is_anomalous = False
            anomaly_score = 0.0

        AccessLog.objects.create(
            owner=request.user,
            user_identifier=user_id,
            endpoint='/api/anomaly-detect/',
            method='POST',
            anomaly_score=anomaly_score,
            is_anomalous=is_anomalous,
            context_vector=input_vector,
        )

        return Response({
            "is_anomalous": is_anomalous,
            "anomaly_score": anomaly_score,
            "user_identifier": user_id,
            "vector_length": len(input_vector),
        }, status=status.HTTP_200_OK)


class BlockchainVerifyView(APIView):
    permission_classes = [AIToolPermission]

    def get(self, request):
        chain = LocalBlockchain.get_chain()
        is_valid = LocalBlockchain.verify_chain()
        return Response({
            "chain_length": len(chain),
            "is_valid": is_valid,
            "chain": chain[-10:],
        })

    def post(self, request):
        is_valid = LocalBlockchain.verify_chain()
        chain = LocalBlockchain.get_chain()
        return Response({
            "verification": "PASS" if is_valid else "FAIL — TAMPERING DETECTED",
            "is_valid": is_valid,
            "chain_length": len(chain),
            "chain": chain,
        }, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────
# API Root
# ──────────────────────────────────────────────

@api_view(['GET'])
@perm_decorator([AllowAny])
def api_root(request):
    from rest_framework.reverse import reverse
    user_role = get_user_role(request) if request.user.is_authenticated else 'anonymous'
    return Response({
        "project": "UrbanSecure AI-ZeroTrust",
        "your_role": user_role,
        "endpoints": {
            "access_logs": reverse('accesslog-list', request=request),
            "audit_logs": reverse('auditlog-list', request=request),
            "abac_policies": reverse('abacpolicy-list', request=request),
            "role_adaptations": reverse('roleadaptation-list', request=request),
            "adapt_role": reverse('adapt-role', request=request),
            "anomaly_detect": reverse('anomaly-detect', request=request),
            "blockchain_verify": reverse('blockchain-verify', request=request),
        },
    })