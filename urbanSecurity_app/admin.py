from django.contrib import admin
from .models import AccessLog, AuditLog, ABACPolicy, RoleAdaptation


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('user_identifier', 'method', 'endpoint', 'role', 'anomaly_score', 'is_anomalous', 'timestamp')
    list_filter = ('method', 'role', 'is_anomalous')
    search_fields = ('user_identifier', 'endpoint')
    readonly_fields = ('timestamp',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'actor', 'block_hash', 'block_index', 'verified', 'timestamp')
    list_filter = ('verified',)
    search_fields = ('action', 'actor')
    readonly_fields = ('timestamp', 'block_hash', 'prev_hash', 'block_index')


@admin.register(ABACPolicy)
class ABACPolicyAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'attribute', 'condition', 'action', 'is_active', 'priority')
    list_filter = ('role', 'action', 'is_active')
    search_fields = ('name', 'description')


@admin.register(RoleAdaptation)
class RoleAdaptationAdmin(admin.ModelAdmin):
    list_display = ('user_identifier', 'old_role', 'new_role', 'adapted_by', 'from_edge', 'timestamp')
    list_filter = ('adapted_by', 'from_edge')
    search_fields = ('user_identifier', 'reason')
    readonly_fields = ('timestamp',)
