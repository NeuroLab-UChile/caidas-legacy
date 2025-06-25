from django.contrib import admin
from ..models import AppActivityLog


@admin.register(AppActivityLog)
class AppActivityLogAdmin(admin.ModelAdmin):
    ordering = ["-date"]
    list_display = ["id", "user", "date", "n_entries", "updated_date", "created_date"]
    list_filter = ["user", "date", "updated_date", "created_date"]
    search_fields = ["user__username"]

    # In detail view, show all fields and a custom one with get_summary object function
    readonly_fields = [
        "created_date",
        "updated_date",
        "get_summary",
    ]
    fieldsets = (
        (
            "Summary",
            {
                "fields": ["get_summary"],
                # "classes": ["collapse"],
            },
        ),
        (
            "Data",
            {
                "fields": [
                    "user",
                    "date",
                    "n_entries",
                    "actions",
                    "created_date",
                    "updated_date",
                ]
            },
        ),
    )

    def get_summary(self, obj):
        """
        Custom method to display the summary of actions in the detail view.
        """
        summary = obj.get_summary()
        return (
            f"User: {summary['user']}\n"
            f"Date: {summary['date']}\n"
            f"Entries: {summary['n_entries']}\n"
            f"Logins: {summary['n_logins']}\n"
            f"Time in app: {summary['time_in_app']} seconds\n"
            f"Time in app: {summary['time_in_app_str']}"
        )

    get_summary.short_description = "Summary of Actions"
