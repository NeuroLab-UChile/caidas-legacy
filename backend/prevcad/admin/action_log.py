from django.contrib import admin
from ..models import ActionLog

@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'user', 'action_type', 'description', 'ip_address']
    list_filter = ['action_type', 'timestamp', 'user']
    search_fields = ['description', 'user__username', 'ip_address']
    readonly_fields = [
        'timestamp', 
        'user', 
        'action_type', 
        'description', 
        'ip_address', 
        'user_agent', 
        'extra_data'
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False 