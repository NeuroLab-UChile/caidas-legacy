from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .user_profile import UserProfile
from .category_template import CategoryTemplate
from django.core.exceptions import ValidationError
from .user_types import UserTypes

class HealthCategory(models.Model):
    STATUS_CHOICES = [
        ('verde', 'Verde'),
        ('amarillo', 'Amarillo'),
        ('rojo', 'Rojo'),
        ('gris', 'Gris'),
    ]

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name="Usuario")
    template = models.ForeignKey(CategoryTemplate, on_delete=models.CASCADE, verbose_name="Plantilla")
    completion_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de completado")
    responses = models.JSONField(null=True, blank=True, verbose_name="Respuestas")
    status_color = models.CharField(max_length=20, choices=STATUS_CHOICES, null=True, blank=True, verbose_name="Color de riesgo")
    is_draft = models.BooleanField(default=True, verbose_name="Es borrador", help_text="Si está marcado, las recomendaciones no serán visibles para el paciente")
    recommendations = models.JSONField(null=True, blank=True, default=dict, help_text="Recomendaciones asociadas al estado actual, en formato JSON")
    use_default_recommendations = models.BooleanField(default=True, verbose_name="Usar recomendaciones por defecto", help_text="Si está marcado, las recomendaciones serán copiadas desde la plantilla asociada.")
    professional_evaluation_results = models.JSONField(
        null=True,
        blank=True,
        default=dict,
        help_text="Resultados de evaluación profesional, en formato JSON"
    )
    can_edit_user_type = models.BooleanField(default=False, verbose_name="Puede editar el tipo de usuario", help_text="Si está marcado, el usuario puede cambiar el tipo de usuario")

    editors = models.ManyToManyField(
        UserProfile,
        through='HealthCategoryEditor',
        related_name='editable_categories',
        blank=True
    )

    class Meta:
        verbose_name = "Categoría de Salud"
        verbose_name_plural = "Categorías de Salud"
        ordering = ['-completion_date']

    def save(self, *args, **kwargs):
        if self.use_default_recommendations and self.template:
            self.recommendations = self.template.default_recommendations
        
        if self.professional_evaluation_results and not self.completion_date:
            self.completion_date = timezone.now()
            
        if not self.professional_evaluation_results and self.template and self.template.evaluation_type == 'PROFESSIONAL':
            self.completion_date = None

        super().save(*args, **kwargs)

    def get_recommendations(self):
        """Retorna las recomendaciones basadas en el estado actual."""
        return self.recommendations.get(self.status_color) if self.recommendations and self.status_color else None

    def update_recommendations(self, status_color, text, user_profile):
        """
        Actualiza las recomendaciones asociadas a un estado específico.
        Solo profesionales pueden actualizar recomendaciones.
        
        Args:
            status_color: Color del estado ('verde', 'amarillo', etc)
            text: Texto de la recomendación
            user_profile: Perfil del usuario que intenta actualizar
            
        Raises:
            ValidationError: Si el usuario no tiene permisos
        """
        # Verificar que sea un profesional
        if not user_profile or user_profile.role == UserTypes.PATIENT:
            raise ValidationError("Solo los profesionales pueden actualizar recomendaciones")

        # Verificar que tenga permisos para editar recomendaciones
        if not self.can_user_edit(user_profile, self.EditableFields.RECOMMENDATIONS):
            raise ValidationError("No tienes permisos para actualizar recomendaciones")

        # Actualizar las recomendaciones
        self.recommendations = self.recommendations or {}
        self.recommendations[status_color] = {
            "text": text,
            "updated_at": timezone.now().isoformat(),
            "professional": {
                "id": user_profile.id,
                "name": f"{user_profile.first_name} {user_profile.last_name}",
                "role": user_profile.role
            }
        }
        
        self.save(update_fields=["recommendations"])

    def can_user_edit(self, user_profile, field=None):
        """
        Verifica si el usuario puede editar esta categoría o un campo específico.
        Basado en el rol del usuario (enfermero o doctor) y las definiciones del template.
        """
        if not user_profile:
            return False

        # Pacientes no pueden editar nada
        if user_profile.role == UserTypes.PATIENT:
            return False

        # Administradores y doctores tienen acceso completo
        if user_profile.role in [UserTypes.ADMIN, UserTypes.DOCTOR]:
            return True

        # Enfermeros solo pueden editar campos específicos definidos en el template
        if user_profile.role == UserTypes.NURSE:
            if field:
                return field in self.template.editable_fields_by_user_type.get(UserTypes.NURSE, [])
            return True  # Si no se especifica un campo, se permite la edición básica

        return False

class HealthCategoryEditor(models.Model):
    """Modelo intermedio para manejar permisos de edición de categorías"""
    category = models.ForeignKey(HealthCategory, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    editable_fields = models.JSONField(
        default=list,
        help_text="Lista de campos que el usuario puede editar"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['category', 'user']

@receiver(post_save, sender=UserProfile)
def create_user_health_categories(sender, instance, created, **kwargs):
    """Crear categorías de salud para un nuevo usuario"""
    if created:
        templates = CategoryTemplate.objects.filter(is_active=True)
        HealthCategory.objects.bulk_create([
            HealthCategory(user=instance, template=template) for template in templates
        ])

@receiver(post_save, sender=CategoryTemplate)
def create_health_categories_for_template(sender, instance, created, **kwargs):
    """Crear categorías de salud cuando se crea un nuevo template"""
    if created:
        users = UserProfile.objects.all()
        HealthCategory.objects.bulk_create([
            HealthCategory(user=user, template=instance) for user in users
        ])

@receiver(pre_delete, sender=CategoryTemplate)
def delete_related_health_categories(sender, instance, **kwargs):
    """Eliminar todas las categorías de salud asociadas cuando se elimina un template"""
    HealthCategory.objects.filter(template=instance).delete()
