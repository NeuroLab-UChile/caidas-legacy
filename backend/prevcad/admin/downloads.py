from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from ..models import DownloadableContent, DownloadByUser


@admin.register(DownloadableContent)
class DownloadableContentAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "file", "created_date", "updated_date"]
    list_filter = ["created_date", "updated_date"]
    search_fields = ["description", "title"]


@admin.register(DownloadByUser)
class DownloadByUserAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "content_link",
        "downloaded",
        "download_date",
        "created_date",
        "updated_date",
    ]
    list_filter = ["downloaded", "download_date"]
    search_fields = ["user__username", "content__title"]

    def content_link(self, obj):
        """
        Returns a link to the content's admin page.
        """
        # if obj.content:
        #     return mark_safe(
        #         f'<a href="{obj.content.get_absolute_url()}">{obj.content}</a>'
        #     )
        # return "No Content"
        return format_html(
            '<a href="/admin/prevcad/downloadablecontent/{}/change/">{}</a>',
            obj.content.id,
            obj.content,
        )

    content_link.short_description = "Content"
    content_link.admin_order_field = "content__title"
