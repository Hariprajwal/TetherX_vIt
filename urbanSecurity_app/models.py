from django.db import models
from django.utils import timezone


class AccessLog(models.Model):
    """Logs every API access for anomaly detection and auditing."""
    user_identifier = models.CharField(max_length=255, default='anonymous')
    endpoint = models.CharField(max_length=500)
    method = models.CharField(max_length=10)  # GET, POST, PUT, DELETE
    role = models.CharField(max_length=100, default='viewer')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    anomaly_score = models.FloatField(default=0.0)
    is_anomalous = models.BooleanField(default=False)
    context_vector = models.JSONField(null=True, blank=True)  # The 5-feature vector
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.user_identifier} → {self.method} {self.endpoint}"


class AuditLog(models.Model):
    """Blockchain-integrated tamper-proof audit trail."""
    action = models.CharField(max_length=255)
    actor = models.CharField(max_length=255, default='system')
    details = models.TextField(blank=True, default='')
    block_hash = models.CharField(max_length=64)
    prev_hash = models.CharField(max_length=64, default='0' * 64)
    block_index = models.IntegerField(default=0)
    timestamp = models.DateTimeField(default=timezone.now)
    verified = models.BooleanField(default=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[Block #{self.block_index}] {self.action} by {self.actor}"


class ABACPolicy(models.Model):
    """Attribute-Based Access Control policy rules (zero-trust)."""
    ACTIONS = [
        ('allow', 'Allow'),
        ('deny', 'Deny'),
        ('elevate', 'Elevate Role'),
        ('downgrade', 'Downgrade Role'),
    ]
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, default='')
    role = models.CharField(max_length=100)
    attribute = models.CharField(max_length=255)  # e.g. 'time_of_day', 'ip_range', 'location'
    condition = models.CharField(max_length=500)   # e.g. 'hour >= 20', 'ip not in 10.0.0.0/8'
    action = models.CharField(max_length=20, choices=ACTIONS, default='deny')
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)  # Higher = evaluated first
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority']
        verbose_name_plural = 'ABAC Policies'

    def __str__(self):
        return f"{self.name}: IF role={self.role} AND {self.attribute} {self.condition} → {self.action}"


class RoleAdaptation(models.Model):
    """Records MAS-driven role adaptations."""
    user_identifier = models.CharField(max_length=255)
    old_role = models.CharField(max_length=100)
    new_role = models.CharField(max_length=100)
    context_vector = models.JSONField(null=True, blank=True)
    reason = models.TextField(blank=True, default='')
    adapted_by = models.CharField(max_length=50, default='edge')  # 'edge', 'local', 'agent'
    from_edge = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user_identifier}: {self.old_role} → {self.new_role} ({self.adapted_by})"
