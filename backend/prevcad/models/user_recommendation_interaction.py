from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class UserRecommendationInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recommendation = models.ForeignKey('TextRecomendation', on_delete=models.CASCADE)
    clicks = models.IntegerField(default=1)
    last_clicked = models.DateTimeField(default=timezone.now)
    first_seen = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recommendation')
        indexes = [
            models.Index(fields=['user', 'recommendation']),
            models.Index(fields=['last_clicked']),
        ]