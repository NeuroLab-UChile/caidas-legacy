from django.db import models
from django.utils import timezone

class EvaluationForm(models.Model):
    health_category = models.OneToOneField(
        'HealthCategory', 
        on_delete=models.CASCADE,
        related_name='evaluation_form'
    )
    question_nodes = models.JSONField(
        default=dict,
        help_text="Estructura de nodos de preguntas",
        null=True,
        blank=True
    )
    professional_responses = models.JSONField(
        null=True,
        blank=True,
        help_text="Respuestas del profesional"
    )
    responses = models.JSONField(
        null=True,
        blank=True,
        help_text="Respuestas del usuario"
    )
    completed_date = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Evaluación de {self.health_category}" 

    class Meta:
        verbose_name = "Formulario de Evaluación"
        verbose_name_plural = "Formularios de Evaluación" 