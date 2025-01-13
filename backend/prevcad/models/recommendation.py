from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.conf import settings

class Recommendation(models.Model):
    health_category = models.OneToOneField(
        'HealthCategory',
        on_delete=models.CASCADE,
        related_name='recommendation'
    )
    text = models.TextField(blank=True, null=True)
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
    video = models.FileField(
        upload_to='recommendations/videos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['mp4', 'mov', 'avi', 'webm']
            )
        ]
    )
    is_draft = models.BooleanField(default=True)
    use_default = models.BooleanField(default=False)
    updated_by = models.CharField(max_length=255, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    

   

    def __str__(self):
        return f"Recomendación para {self.health_category}" 

    def save(self, *args, **kwargs):
        if not self.status_color:
            self.status_color = 'gris'
            
        # Si hay un nuevo video y ya existe uno, eliminar el anterior
        if self.pk:
            try:
                old_instance = Recommendation.objects.get(pk=self.pk)
                if old_instance.video and self.video != old_instance.video:
                    old_instance.video.delete(save=False)
            except Recommendation.DoesNotExist:
                pass
                
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Eliminar el archivo de video cuando se elimina la recomendación
        if self.video:
            self.video.delete(save=False)
        super().delete(*args, **kwargs) 

