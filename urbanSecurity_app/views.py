# urbanSecurity_app/views.py
import requests
import logging
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import AccessLog, AuditLog, ABACPolicy, RoleAdaptation
from .serializers import (
    AccessLogSerializer, AuditLogSerializer,
    ABACPolicySerializer, RoleAdaptationSerializer,
    AdaptRoleRequestSerializer, AnomalyDetectRequestSerializer,
)
from .blockchain import LocalBlockchain

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# CRUD ViewSets (GET, POST, PUT, PATCH, DELETE)
# ──────────────────────────────────────────────

class AccessLogViewSet(viewsets.ModelViewSet):
    """CRUD for Access Logs — tracks every API request with anomaly scores."""
    queryset = AccessLog.objects.all()
    serializer_class = AccessLogSerializer


class AuditLogViewSet(viewsets.ModelViewSet):
    """CRUD for Audit Logs — blockchain-integrated tamper-proof trail."""
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer

    def perform_create(self, serializer):
        """Auto-generate blockchain hash on create."""
        action = serializer.validated_data.get('action', '')
        actor = serializer.validated_data.get('actor', 'system')
        details = serializer.validated_data.get('details', '')
        data_str = f"{action}|{actor}|{details}"
        block = LocalBlockchain.add_block(data_str)
        serializer.save(
            block_hash=block['hash'],
            prev_hash=block['prev_hash'],
            block_index=block['index'],
            verified=True,
        )


class ABACPolicyViewSet(viewsets.ModelViewSet):
    """CRUD for ABAC Zero-Trust policies — granular, context-aware rules."""
    queryset = ABACPolicy.objects.all()
    serializer_class = ABACPolicySerializer


class RoleAdaptationViewSet(viewsets.ModelViewSet):
    """CRUD for MAS Role Adaptations — records AI-driven role changes."""
    queryset = RoleAdaptation.objects.all()
    serializer_class = RoleAdaptationSerializer


# ──────────────────────────────────────────────
# Custom Action Endpoints
# ──────────────────────────────────────────────

class AdaptRoleView(APIView):
    """
    POST: Predict optimal role using edge ML (LSTM) or local fallback.
    Sends context vector to Flask edge node; falls back to local inference.
    """
    serializer_class = AdaptRoleRequestSerializer  # For DRF browsable API form

    def get(self, request):
        """Display usage info in the browsable API."""
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
            ]
        })

    def post(self, request):
        serializer = AdaptRoleRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        context = serializer.validated_data['context']
        user_id = serializer.validated_data.get('user_identifier', 'anonymous')
        current_role = serializer.validated_data.get('current_role', 'viewer')

        recommended_role = None
        from_edge = False

        try:
            # Try edge node first (low-latency simulation)
            edge_url = "http://localhost:5001/edge-predict"
            resp = requests.post(edge_url, json={"context": context}, timeout=2)
            resp.raise_for_status()
            edge_data = resp.json()
            recommended_role = edge_data.get("recommended_role")
            from_edge = True
            edge_status = edge_data.get("status")
        except Exception:
            # Fallback to local prediction
            try:
                from .utils.RoleLSTM import RolePredictor
                recommended_role = RolePredictor.predict(context)
                from_edge = False
                edge_status = "edge_unavailable_local_fallback"
            except Exception as e:
                logger.error(f"Both edge and local prediction failed: {e}")
                recommended_role = "normal"
                edge_status = f"fallback_default: {str(e)}"

        # Record the adaptation
        RoleAdaptation.objects.create(
            user_identifier=user_id,
            old_role=current_role,
            new_role=recommended_role,
            context_vector=context,
            reason=edge_status,
            adapted_by='edge' if from_edge else 'local',
            from_edge=from_edge,
        )

        # Log to blockchain
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
    """
    POST: Run anomaly detection using the Autoencoder DL model.
    Returns anomaly score and whether the input is flagged as anomalous.
    """
    serializer_class = AnomalyDetectRequestSerializer

    def get(self, request):
        return Response({
            "info": "POST an input_vector to detect anomalies",
            "example_body": {
                "input_vector": [0.8, 0.3, 1.0, 0.5, 0.2],
                "user_identifier": "sensor_42"
            }
        })

    def post(self, request):
        serializer = AnomalyDetectRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        input_vector = serializer.validated_data['input_vector']
        user_id = serializer.validated_data.get('user_identifier', 'anonymous')

        try:
            from .utils.RoleLSTM import AnomalyDetector
            detector = AnomalyDetector()
            is_anomalous = detector.detect(input_vector)
            anomaly_score = 0.85 if is_anomalous else 0.05  # Simplified score
        except Exception as e:
            logger.warning(f"Anomaly detection model unavailable: {e}")
            is_anomalous = False
            anomaly_score = 0.0

        # Record access log
        AccessLog.objects.create(
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
    """
    GET/POST: Verify integrity of the entire blockchain audit trail.
    """

    def get(self, request):
        chain = LocalBlockchain.get_chain()
        is_valid = LocalBlockchain.verify_chain()
        return Response({
            "chain_length": len(chain),
            "is_valid": is_valid,
            "chain": chain[-10:],  # Last 10 blocks
            "info": "POST to this endpoint to run a full verification"
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
# API Root Info
# ──────────────────────────────────────────────

@api_view(['GET'])
def api_root(request):
    """UrbanSecure AI-ZeroTrust — API Overview."""
    from rest_framework.reverse import reverse
    return Response({
        "project": "UrbanSecure AI-ZeroTrust",
        "description": "AI-Enhanced Zero-Trust Security Layer with Blockchain-Integrated Logging",
        "endpoints": {
            "access_logs": reverse('accesslog-list', request=request),
            "audit_logs": reverse('auditlog-list', request=request),
            "abac_policies": reverse('abacpolicy-list', request=request),
            "role_adaptations": reverse('roleadaptation-list', request=request),
            "adapt_role": reverse('adapt-role', request=request),
            "anomaly_detect": reverse('anomaly-detect', request=request),
            "blockchain_verify": reverse('blockchain-verify', request=request),
        },
        "components": [
            "Multi-Agent Systems (MAS) — Dynamic Role Management",
            "Deep Learning (DL) — Real-Time Anomaly Detection",
            "Blockchain — Tamper-Proof Audit Logs",
            "ABAC + Zero-Trust — Granular Context-Aware Restrictions",
            "Edge Computing — Low-Latency Decisions",
        ]
    })