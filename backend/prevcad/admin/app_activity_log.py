from django.contrib import admin
from ..models import AppActivityLog


@admin.register(AppActivityLog)
class AppActivityLogAdmin(admin.ModelAdmin):
    ordering = ["-timestamp"]
    list_display = ["id", "user", "action", "timestamp"]
    list_filter = ["action", "timestamp", "user"]
    search_fields = ["description", "user__username", "ip_address"]
