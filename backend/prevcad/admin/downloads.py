from django.contrib import admin
from ..models import DownloadableContent, DownloadByUser


@admin.register(DownloadableContent)
class DownloadableContentAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "file", "created_date", "updated_date"]
    list_filter = ["created_date", "updated_date"]
    search_fields = ["description", "title"]


@admin.register(DownloadByUser)
class DownloadByUserAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "content", "download_date"]
    list_filter = ["download_date"]
    search_fields = ["user__username", "content__title"]
