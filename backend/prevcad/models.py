from typing import Any
from django.db import models
from django.utils.encoding import smart_str

class Card(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    image = models.CharField(max_length=500)
    description = models.TextField(max_length=10000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args: Any, **kwargs: Any) -> None:
        # Asegurar que los campos de texto están correctamente codificados
        self.name = smart_str(self.name)
        self.image = smart_str(self.image)
        self.description = smart_str(self.description)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class HealthCategory(Card):
    icon = models.CharField(max_length=500)

    def save(self, *args: Any, **kwargs: Any) -> None:
        # Asegurar que el campo 'icon' está correctamente codificado
        self.icon = smart_str(self.icon)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'health_categories'


class HealthRecommendation(Card):
    health_category = models.ForeignKey('HealthCategory', on_delete=models.CASCADE)
    result = models.TextField()
    view_info = models.TextField()

    def save(self, *args: Any, **kwargs: Any) -> None:
        # Asegurar que los campos de texto están correctamente codificados
        self.result = smart_str(self.result)
        self.view_info = smart_str(self.view_info)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class WorkRecommendation(HealthRecommendation):
    health_category = models.ForeignKey('HealthCategory', related_name='work_recommendations', on_delete=models.CASCADE)
    work_specific_field = models.CharField(max_length=100)

    def save(self, *args: Any, **kwargs: Any) -> None:
        # Asegurar que el campo 'work_specific_field' está correctamente codificado
        self.work_specific_field = smart_str(self.work_specific_field)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'work_recommendations'


class EvaluationRecommendation(HealthRecommendation):
    health_category = models.ForeignKey('HealthCategory', related_name='evaluation_recommendations', on_delete=models.CASCADE)
    evaluation_specific_field = models.CharField(max_length=100)

    def save(self, *args: Any, **kwargs: Any) -> None:
        # Asegurar que el campo 'evaluation_specific_field' está correctamente codificado
        self.evaluation_specific_field = smart_str(self.evaluation_specific_field)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'evaluation_recommendations'


class TextRecomendation(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100)
    inside_text = models.CharField(max_length=200)

    def save(self, *args: Any, **kwargs: Any) -> None:
        # Asegurar que los campos de texto están correctamente codificados
        self.title = smart_str(self.title)
        self.inside_text = smart_str(self.inside_text)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'text_recomendation'
