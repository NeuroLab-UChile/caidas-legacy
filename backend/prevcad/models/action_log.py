from django.db import models
from django.conf import settings
from django.utils import timezone

class ActionLog(models.Model):
    """Modelo para registrar acciones realizadas en el sistema"""
    
    ACTION_TYPES = [
        ('CREATE', 'Creación'),
        ('UPDATE', 'Actualización'),
        ('DELETE', 'Eliminación'),
        ('VIEW', 'Visualización'),
        ('LOGIN', 'Inicio de sesión'),
        ('LOGOUT', 'Cierre de sesión'),
        ('UPLOAD', 'Subida de archivo'),
        ('DOWNLOAD', 'Descarga de archivo'),
        ('OTHER', 'Otra acción'),
    ]

    timestamp = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuario"
    )
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        verbose_name="Tipo de acción"
    )
    description = models.TextField(
        verbose_name="Descripción"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP"
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name="User Agent"
    )
    extra_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos adicionales"
    )

    class Meta:
        verbose_name = "Registro de Acción"
        verbose_name_plural = "Registro de Acciones"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user']),
            models.Index(fields=['action_type']),
        ]

    def __str__(self):
        user_str = self.user.username if self.user else 'Sistema'
        return f"{self.get_action_type_display()} por {user_str} en {self.timestamp}" 