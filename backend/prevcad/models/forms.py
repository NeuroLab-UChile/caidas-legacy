from typing import Any
from django.db import models
from django.contrib.auth.models import User
from .physical_activity import PhysicalActivity


class Form(models.Model):

  class TYPE_CHOICES(models.TextChoices):
    TEST = "TEST", "Test"

  category = models.ForeignKey(PhysicalActivity, on_delete=models.CASCADE, related_name='forms')
  title = models.CharField(max_length=255)
  description = models.TextField()
  type = models.CharField(max_length=50, choices=TYPE_CHOICES.choices, null=True, blank=True)


  def __str__(self):
    return f"Formulario: {self.title} (Categoría: {self.category.name})"


class FormQuestion(models.Model):
  form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='questions')
  question_text = models.CharField(max_length=1000)
  question_type = models.CharField(max_length=20, choices=[('text', 'Texto'), ('multiple_choice', 'Selección múltiple')])
  options = models.JSONField(null=True, blank=True)

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

  answer_text = models.TextField(null=True, blank=True)
  selected_option = models.CharField(max_length=100, null=True, blank=True)

  def __str__(self):
    return f"Respuesta de {self.form_response.user.username} a la pregunta {self.question.question_text}"

