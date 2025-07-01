from django.db import models
from django.conf import settings
from django.utils import timezone
import datetime
from typing import (
    Any,
    List,
    cast,
    Dict,
    Optional,
    Union,
    Type,
    Literal,
    Optional,
    LiteralString,
)


# DownloadableContent class
class DownloadableContent(models.Model):
    """Modelo para registrar contenido descargable"""

    class Meta:
        verbose_name = "Contenido Descargable"
        verbose_name_plural = "Contenidos Descargables"
        ordering = ["-created_date"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["created_date"]),
        ]

    title = models.CharField(max_length=512, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descripción")
    file = models.FileField(upload_to="downloadable_content/", verbose_name="Archivo")
    created_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_date = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f"/downloadable_content/{self.id}/"

    def get_file_url(self):
        return self.file.url if self.file else None


class DownloadByUser(models.Model):
    """Modelo para registrar descargas por usuario"""

    class Meta:
        verbose_name = "Descarga por Usuario"
        verbose_name_plural = "Descargas por Usuario"
        ordering = ["-download_date"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["download_date"]),
        ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Usuario",
    )
    content = models.ForeignKey(
        DownloadableContent,
        on_delete=models.CASCADE,
        verbose_name="Contenido Descargable",
    )
    download_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Descarga"
    )

    def __str__(self):
        return f"{self.user.username} - {self.content.title}"
