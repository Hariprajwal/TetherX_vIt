from rest_framework import serializers
from .models import AccessLog, AuditLog, ABACPolicy, RoleAdaptation


class AccessLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessLog
        fields = '__all__'
        read_only_fields = ['timestamp']


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = ['timestamp', 'block_hash', 'prev_hash', 'block_index', 'verified']


class ABACPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = ABACPolicy
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class RoleAdaptationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleAdaptation
        fields = '__all__'
        read_only_fields = ['timestamp']


# --- Request serializers for custom action endpoints ---

class AdaptRoleRequestSerializer(serializers.Serializer):
    context = serializers.ListField(
        child=serializers.FloatField(),
        min_length=5,
        max_length=5,
        help_text="Context vector of exactly 5 floats for role prediction"
    )
    user_identifier = serializers.CharField(max_length=255, default='anonymous')
    current_role = serializers.CharField(max_length=100, default='viewer')


class AnomalyDetectRequestSerializer(serializers.Serializer):
    input_vector = serializers.ListField(
        child=serializers.FloatField(),
        help_text="Input feature vector for anomaly detection"
    )
    user_identifier = serializers.CharField(max_length=255, default='anonymous')


class BlockchainVerifyRequestSerializer(serializers.Serializer):
    """No input needed — verifies the entire chain."""
    pass
