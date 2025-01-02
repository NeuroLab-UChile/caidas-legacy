from django.db import models
from django.utils import timezone

class Recommendation(models.Model):
    STATUS_CHOICES = [
        ('verde', 'Verde'),
        ('amarillo', 'Amarillo'),
        ('rojo', 'Rojo'),
        ('gris', 'Gris'),
    ]

    health_category = models.OneToOneField(
        'HealthCategory', 
        on_delete=models.CASCADE,
        related_name='recommendation'
    )
    status_color = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='gris'
    )
    text = models.TextField(
        null=True,
        blank=True
    )
    updated_by = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)
    is_draft = models.BooleanField(default=True)

    def __str__(self):
        return f"Recomendación para {self.health_category}" 