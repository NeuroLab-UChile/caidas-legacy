from typing import Any
from django.db import models
from django.utils.encoding import smart_str
from django.contrib.auth.models import User

class Card(models.Model):
  name = models.CharField(max_length=100)
  image = models.ImageField(name='image', upload_to='health_categories_images/')
  description = models.TextField(max_length=10000)

  def save(self, *args: Any, **kwargs: Any) -> None:
    # Asegurar que los campos de texto están correctamente codificados
    self.name = smart_str(self.name)
    self.description = smart_str(self.description)
    super().save(*args, **kwargs)

  def upload_to(self, instance: Any, filename: str) -> str:
    return f'{instance.__class__.__name__}/{filename}'

  def __str__(self):
    return self.name

  class Meta:
    abstract = True


class HealthCategory(Card):
  icon = models.ImageField(upload_to='health_categories_icons/')

  def save(self, *args: Any, **kwargs: Any) -> None:
    super().save(*args, **kwargs)

  class Meta:
    db_table = 'health_categories'


class HealthRecommendation(Card):
  health_category = models.ForeignKey('HealthCategory', on_delete=models.CASCADE)
  result = models.TextField()
  view_info = models.TextField()

  def save(self, *args: Any, **kwargs: Any) -> None:
    self.result = smart_str(self.result)
    self.view_info = smart_str(self.view_info)
    super().save(*args, **kwargs)

  def __str__(self):
    return f"Recomendación para {self.health_category.name}"

  class Meta:
    abstract = True


class WorkRecommendation(HealthRecommendation):
  health_category = models.ForeignKey('HealthCategory', related_name='work_recommendations', on_delete=models.CASCADE)
  work_specific_field = models.CharField(max_length=100)

  def save(self, *args: Any, **kwargs: Any) -> None:
    self.work_specific_field = smart_str(self.work_specific_field)
    super().save(*args, **kwargs)

  def __str__(self):
    return f"Recomendación de trabajo para {self.health_category.name}"

  class Meta:
    db_table = 'work_recommendations'


class EvaluationRecommendation(HealthRecommendation):
  health_category = models.ForeignKey('HealthCategory', related_name='evaluation_recommendations', on_delete=models.CASCADE)
  evaluation_specific_field = models.CharField(max_length=100)

  def save(self, *args: Any, **kwargs: Any) -> None:
    self.evaluation_specific_field = smart_str(self.evaluation_specific_field)
    super().save(*args, **kwargs)

  def __str__(self):
    return f"Evaluación para {self.health_category.name}"

  class Meta:
    db_table = 'evaluation_recommendations'


from django.db import models

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
  
 
class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

  def save(self, *args: Any, **kwargs: Any) -> None:
    super().save(*args, **kwargs)

  def __str__(self):
    return self.user.username


class Form(models.Model):

  class TYPE_CHOICES(models.TextChoices):
    TEST = "TEST", "Test"

  category = models.ForeignKey(HealthCategory, on_delete=models.CASCADE, related_name='forms')
  title = models.CharField(max_length=255)
  description = models.TextField()
  type = models.CharField(max_length=50, choices=TYPE_CHOICES.choices, null=True, blank=True)

  def __str__(self):
    return f"Formulario: {self.title} (Categoría: {self.category.name})"



class FormQuestion(models.Model):
  form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='questions')
  question_text = models.CharField(max_length=1000)
  question_type = models.CharField(max_length=20, choices=[('text', 'Texto'), ('multiple_choice', 'Selección múltiple')])
  options = models.JSONField(null=True, blank=True)  # Almacena las opciones como JSON

  def __str__(self):
    return f"Pregunta: {self.question_text} (Formulario: {self.form.category.name})"


class FormResponse(models.Model):
  form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='responses')
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  def __str__(self):
    return f"Respuesta de {self.user.username} para el formulario {self.form.title}"


class QuestionResponse(models.Model):
  form_response = models.ForeignKey(FormResponse, on_delete=models.CASCADE, related_name='question_responses')
  question = models.ForeignKey(FormQuestion, on_delete=models.CASCADE)
  
  # Diferentes tipos de respuestas según el tipo de pregunta
  answer_text = models.TextField(null=True, blank=True)  # Para preguntas de texto
  selected_option = models.CharField(max_length=100, null=True, blank=True)  # Para preguntas de selección múltiple

  def __str__(self):
    return f"Respuesta de {self.form_response.user.username} a la pregunta {self.question.question_text}"

