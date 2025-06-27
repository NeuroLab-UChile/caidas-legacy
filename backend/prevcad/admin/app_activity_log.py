import json
import logging
from django.forms import widgets
from django.contrib import admin
from django.db.models import JSONField
from ..models import AppActivityLog

logger = logging.getLogger(__name__)


# https://stackoverflow.com/questions/48145992/showing-json-field-in-django-admin
class PrettyJSONWidget(widgets.Textarea):

    def format_value(self, value):
        try:
            value = json.dumps(json.loads(value), indent=2, sort_keys=True)
            # these lines will try to adjust size of TextArea to fit to content
            row_lengths = [len(r) for r in value.split("\n")]
            self.attrs["rows"] = min(max(len(row_lengths) + 2, 10), 30)
            self.attrs["cols"] = min(max(max(row_lengths) + 2, 40), 120)
            return value
        except Exception as e:
            logger.warning("Error while formatting JSON: {}".format(e))
            return super(PrettyJSONWidget, self).format_value(value)


@admin.register(AppActivityLog)
class AppActivityLogAdmin(admin.ModelAdmin):
    ordering = ["-date"]
    list_display = [
        "id",
        "user",
        "date",
        "n_entries",
        "n_logins",
        "time_in_app_str",
        "updated_date",
        "created_date",
    ]
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
                    # "n_entries",
                    "created_date",
                    "updated_date",
                    "actions",
                ]
            },
        ),
    )

    formfield_overrides = {JSONField: {"widget": PrettyJSONWidget}}

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
