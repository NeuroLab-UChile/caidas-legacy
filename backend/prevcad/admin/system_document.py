from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.utils.text import Truncator  # for shortening a text
from ..models import SystemDocument


@admin.register(SystemDocument)
class SystemDocumentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "category",
        "show_free_text",
        "file",
        "editor",
        "updated_date",
        "created_date",
    ]
    list_filter = ["category", "editor", "created_date", "updated_date"]
    search_fields = ["free_text", "name"]

    @admin.display(description="Texto Libre")
    def show_free_text(self, obj: SystemDocument) -> str:
        #  https://stackoverflow.com/questions/62241862/django-admin-list-display-show-full-text-on-mouse-hover
        # https://stackoverflow.com/questions/70485017/django-admin-drop-down-with-very-long-description-text
        return format_html(
            '<span class="truncated_text" title="{txt}">{txt_short}</span>',
            txt=obj.free_text,
            txt_short=Truncator(str(obj.free_text)).chars(25),  # .words(3),
        )
