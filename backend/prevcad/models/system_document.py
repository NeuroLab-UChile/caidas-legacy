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

# SystemDocument class
# Campos (a inglés):
#     Nombre
#     Editor
#     Texto libre
#     Archivo
#     Fecha edición


class SystemDocument(models.Model):
    """Modelo para documentos del sistema"""

    class Meta:
        verbose_name = "Documento del Sistema"
        verbose_name_plural = "Documentos del Sistema"
        ordering = ["-updated_date"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["updated_date"]),
        ]

    name = models.CharField(max_length=512, verbose_name="Nombre")
    category = models.CharField(max_length=128, blank=True, verbose_name="Categoría")
    free_text = models.TextField(blank=True, verbose_name="Texto Libre")
    file = models.FileField(upload_to="system_documents/", verbose_name="Archivo")
    editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="system_documents",
        verbose_name="Editor",
    )
    updated_date = models.DateTimeField(auto_now=True, verbose_name="Fecha de Edición")
    created_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )

    def __str__(self):
        return f"[{self.id}] {self.name} - {self.category}"
