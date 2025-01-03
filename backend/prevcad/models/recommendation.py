from django.db import models
from django.utils import timezone

class Recommendation(models.Model):
    health_category = models.OneToOneField(
        'HealthCategory',
        on_delete=models.CASCADE,
        related_name='recommendation'
    )
    text = models.TextField(blank=True)
    default_text = models.TextField(blank=True)
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
    default_status_color = models.CharField(
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
    is_signed = models.BooleanField(default=False)
    signed_by = models.CharField(max_length=150, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    updated_by = models.CharField(max_length=255, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    use_default = models.BooleanField(default=False)
    professional_name = models.CharField(max_length=255, null=True, blank=True)
    professional_role = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Si es nuevo y no tiene texto, usar el texto por defecto
        if not self.pk and not self.text:
            self.text = self.default_text
            self.status_color = self.default_status_color
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Recomendación para {self.health_category}" 