from typing import Any
from django.db import models
from django.utils.encoding import smart_str
from django.contrib.auth.models import User

class Card(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    image = models.ImageField(name='image', upload_to='health_categories_images/')  # Cambié a ImageField
    description = models.TextField(max_length=10000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args: Any, **kwargs: Any) -> None:
        # Asegurar que los campos de texto están correctamente codificados
        self.name = smart_str(self.name)
     
        self.description = smart_str(self.description)
        super().save(*args, **kwargs)

    def upload_to(self, instance: Any, filename: str) -> str:
        return f'{instance.__class__.__name__}/{filename}'
    

    class Meta:
        abstract = True


class HealthCategory(Card):
    icon = models.ImageField(upload_to='health_categories_icons/')  # Cambié a ImageField

    def save(self, *args: Any, **kwargs: Any) -> None:
        # Asegurar que el campo 'icon' está correctamente codificado
      
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
class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

  def save(self, *args: Any, **kwargs: Any) -> None:
    # Guardar el perfil, no es necesario smart_str aquí ya que es una imagen
    super().save(*args, **kwargs)

  def __str__(self):
    return self.user.username