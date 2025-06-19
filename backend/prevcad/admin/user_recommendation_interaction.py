from django.contrib import admin
from ..models import UserRecommendationInteraction


@admin.register(UserRecommendationInteraction)
class UserRecommendationInteractionAdmin(admin.ModelAdmin):
    ordering = ["-last_clicked"]
    list_display = [
        "id",
        "user",
        "recommendation",
        "clicks",
        "last_clicked",
        "first_seen",
    ]
    list_filter = ["last_clicked", "first_seen", "user"]
    search_fields = ["user__username"]
