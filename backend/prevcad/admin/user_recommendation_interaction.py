from django.contrib import admin
from django.utils.html import format_html
from ..models import UserRecommendationInteraction


@admin.register(UserRecommendationInteraction)
class UserRecommendationInteractionAdmin(admin.ModelAdmin):
    ordering = ["-last_clicked"]
    list_display = [
        "id",
        "user",
        # "recommendation",
        "recommendation_link",
        "clicks",
        "last_clicked",
        "first_seen",
    ]
    list_filter = ["last_clicked", "first_seen", "user"]
    search_fields = ["user__username"]

    def recommendation_link(self, obj):
        return format_html(
            '<a href="/admin/prevcad/textrecomendation/{}/change/">Recomendación {}</a>',
            obj.recommendation.id,
            obj.recommendation.id,
        )
