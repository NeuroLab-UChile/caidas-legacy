from django.db import models
from django.conf import settings
from django.utils import timezone


class AppActivityLog(models.Model):
    """Modelo para registrar actividades de la aplicación"""

    class Meta:
        verbose_name = "Registro de Actividad de la Aplicación"
        verbose_name_plural = "Registros de Actividad de la Aplicación"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["user"]),
        ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        verbose_name="Usuario",
    )
    action = models.CharField(max_length=255, verbose_name="Acción")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="Fecha y hora")
