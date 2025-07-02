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
from django.core.exceptions import ValidationError
from . import User


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
        return f"[{self.id}] {self.title}"

    def get_absolute_url(self):
        return f"{settings.MEDIA_URL}{self.file}"

    def get_file_url(self):
        return self.file.url if self.file else None

    def get_or_create_download_for_user(self, user: User) -> "DownloadByUser":
        """
        Get or create a DownloadByUser instance for the given user and content.
        """
        download, created = DownloadByUser.objects.get_or_create(
            user=user, content=self
        )
        return download


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
        # Set unique constraint to prevent duplicate downloads of the same content by the same user
        constraints = [
            models.UniqueConstraint(
                fields=["user", "content"],
                name="unique_user_content_download",
                violation_error_message="El usuario ya ha descargado este contenido.",
            )
        ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        verbose_name="Usuario",
    )
    content = models.ForeignKey(
        DownloadableContent,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        verbose_name="Contenido Descargable",
    )
    downloaded = models.BooleanField(
        default=False,
        verbose_name="Descargado",
        help_text="Indica si el contenido ha sido descargado",
    )
    download_date = models.DateTimeField(
        blank=True, null=True, verbose_name="Fecha de Descarga"
    )
    updated_date = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización"
    )
    created_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )

    def __str__(self):
        return f"{self.user.username} - {self.content.title}"

    @classmethod
    def get_all_downloads_for_user(cls, user: User) -> List["DownloadByUser"]:
        """
        Get all downloadable content for a specific user, ensuring that each content
        available for download is created for the user if it does not exist.
        """
        return [
            d.get_or_create_download_for_user(user)
            for d in DownloadableContent.objects.all()
        ]
