from typing import Any
from django.db import models
from django.utils.encoding import smart_str


class TextRecomendation(models.Model):
    theme = models.CharField(max_length=100, default='')  # theme (Templado)
    category = models.CharField(max_length=100, default='')  # Categoría
    sub_category = models.CharField(max_length=100, blank=True, null=True, default='')  # Sub-categoría
    learn = models.TextField(blank=True, null=True, default='')  # ¿Sabía qué?
    remember = models.TextField(blank=True, null=True, default='')  # remember!
    data = models.TextField(blank=True, null=True, default='')  # data
    practic_data = models.TextField(blank=True, null=True, default='')  # data práctico
    context_explanation = models.TextField(blank=True, null=True, default='')  # Contexto/Explicación
    quote_link = models.URLField(blank=True, null=True, default='')  # Link (zbib.org para citas APA)
    keywords = models.CharField(max_length=255, blank=True, null=True, default='')  # Keywords

    def save(self, *args: Any, **kwargs: Any) -> None:
        # Asegurar que los campos de texto están correctamente codificados
        self.theme = smart_str(self.theme)
        self.category = smart_str(self.category)
        self.sub_category = smart_str(self.sub_category)
        self.learn = smart_str(self.learn)
        self.remember = smart_str(self.remember)
        self.data = smart_str(self.data)
        self.practic_data = smart_str(self.practic_data)
        self.context_explanation = smart_str(self.context_explanation)
        self.quote_link = smart_str(self.quote_link)
        self.keywords = smart_str(self.keywords)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'text_recomendation'
        indexes = [
            models.Index(fields=['theme']),
            models.Index(fields=['category']),
            models.Index(fields=['sub_category']),
        ]
