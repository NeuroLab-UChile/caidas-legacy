from django.db import models
from django.utils import timezone

class Recommendation(models.Model):
    health_category = models.OneToOneField(
        'HealthCategory',
        on_delete=models.CASCADE,
        related_name='recommendation'
    )
    text = models.TextField(blank=True, default='')
    status_color = models.CharField(
        max_length=20,
        choices=[
            ('verde', 'Verde'),
            ('amarillo', 'Amarillo'),
            ('rojo', 'Rojo'),
            ('gris', 'Gris')
        ],
        default='gris'
    )
    is_draft = models.BooleanField(default=True)
    use_default = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    signed_by = models.CharField(max_length=255, blank=True, null=True)
    is_signed = models.BooleanField(default=False)
    signed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Recomendación para {self.health_category}" 

    def save(self, *args, **kwargs):
        # Asegurar que status_color nunca sea None
        if not self.status_color:
            self.status_color = 'gris'
        super().save(*args, **kwargs) 