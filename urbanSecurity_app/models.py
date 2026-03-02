# urbanSecurity_app/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import random


# ──────────────────────────────────────────────
# Custom User — replaces default auth.User
# ──────────────────────────────────────────────

class User(AbstractUser):
    """
    Custom user model for UrbanSecure.
    - role: one of viewer/Engineer/Municipal (admin is Django superuser, not a role)
    - is_verified: email OTP verified
    - verification_code: 6-digit OTP
    - email: unique
    """
    ROLE_CHOICES = [
        ('viewer', 'Viewer'),
        ('Engineer', 'Engineer'),
        ('Municipal', 'Municipal'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='viewer')
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    email = models.EmailField(unique=True)

    def generate_code(self):
        """Generate a 6-digit OTP and save."""
        self.verification_code = str(random.randint(100000, 999999))
        self.save()
        return self.verification_code

    def __str__(self):
        return f"{self.username} ({self.get_effective_role()})"

    def get_effective_role(self):
        """Returns 'admin' if superuser, else the role field."""
        if self.is_superuser:
            return 'admin'
        return self.role or 'viewer'


# ──────────────────────────────────────────────
# Access Logs — per-user segregated by user FK
# ──────────────────────────────────────────────

class AccessLog(models.Model):
    """Logs every API access for anomaly detection and auditing."""
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_logs',
                              null=True, blank=True, help_text="The user this log belongs to")
    user_identifier = models.CharField(max_length=255, default='anonymous')
    endpoint = models.CharField(max_length=500)
    method = models.CharField(max_length=10)  # GET, POST, PUT, DELETE
    role = models.CharField(max_length=100, default='viewer')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    anomaly_score = models.FloatField(default=0.0)
    is_anomalous = models.BooleanField(default=False)
    context_vector = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.user_identifier} → {self.method} {self.endpoint}"


# ──────────────────────────────────────────────
# Audit Logs — blockchain-integrated
# ──────────────────────────────────────────────

class AuditLog(models.Model):
    """Blockchain-integrated tamper-proof audit trail."""
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs',
                              null=True, blank=True)
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


# ──────────────────────────────────────────────
# ABAC Policies — Zero-Trust Rules
# ──────────────────────────────────────────────

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
    attribute = models.CharField(max_length=255)
    condition = models.CharField(max_length=500)
    action = models.CharField(max_length=20, choices=ACTIONS, default='deny')
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority']
        verbose_name_plural = 'ABAC Policies'

    def __str__(self):
        return f"{self.name}: IF role={self.role} AND {self.attribute} {self.condition} → {self.action}"


# ──────────────────────────────────────────────
# Role Adaptations — MAS-driven
# ──────────────────────────────────────────────

class RoleAdaptation(models.Model):
    """Records MAS-driven role adaptations."""
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_adaptations',
                              null=True, blank=True)
    user_identifier = models.CharField(max_length=255)
    old_role = models.CharField(max_length=100)
    new_role = models.CharField(max_length=100)
    context_vector = models.JSONField(null=True, blank=True)
    reason = models.TextField(blank=True, default='')
    adapted_by = models.CharField(max_length=50, default='edge')
    from_edge = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user_identifier}: {self.old_role} → {self.new_role} ({self.adapted_by})"
