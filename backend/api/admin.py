from django.contrib import admin
from . import models


@admin.register(models.Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'score', 'severity', 'status', 'created_at', 'reviewed_by', 'reviewed_at')
    list_filter = ('status', 'severity', 'created_at')
    search_fields = ('user__username', 'user__email', 'reason')
    readonly_fields = ('created_at',)


@admin.register(models.AlertAudit)
class AlertAuditAdmin(admin.ModelAdmin):
    list_display = ('id', 'alert', 'action', 'actor', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('note',)
    readonly_fields = ('created_at',)


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'is_admin', 'created_at')
    list_filter = ('is_admin', 'created_at')
    search_fields = ('username', 'email', 'display_name')

