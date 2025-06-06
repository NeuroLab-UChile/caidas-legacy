from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from .user_profile import UserProfile
from .category_template import CategoryTemplate
from .evaluation import EvaluationForm
from .recommendation import Recommendation

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver


class HealthCategoryEditor(models.Model):
    health_category = models.ForeignKey('HealthCategory', on_delete=models.CASCADE)
    editor = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Editor de Categoría de Salud"
        verbose_name_plural = "Editores de Categoría de Salud"
        unique_together = ('health_category', 'editor')

class HealthCategory(models.Model):
    # Campos que siempre son readonly
    class Meta:
        verbose_name = "Perfil de Salud"
        verbose_name_plural = "Perfiles de Salud"
        ordering = ['-evaluation_form__completed_date', 'recommendation__is_draft', '-user__user__last_name', '-template__allowed_editor_roles']

    READONLY_FIELDS = {'user', 'template', 'created_at'}

    user = models.ForeignKey(
        UserProfile, 
        on_delete=models.CASCADE, 
        verbose_name="Usuario"
    )
    template = models.ForeignKey(
        CategoryTemplate, 
        on_delete=models.CASCADE, 
        verbose_name="Plantilla"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    editors = models.ManyToManyField(
        UserProfile,
        through='HealthCategoryEditor',
        related_name='editable_categories',
        blank=True
    )
    evaluation_history = models.JSONField(default=list)
 


    
   

    def __str__(self):
        """Retorna una representación en string más amigable del objeto"""
        try:
            template_name = self.template.name.title()
            
            # Obtener el nombre y rol del usuario
            user_name = self.user.user.get_full_name() or self.user.user.username
            
            status = self.get_status()
            status_indicator = {
                'verde': '✓',
                'amarillo': '⚠',
                'rojo': '!',
                'gris': '•'
            }.get(status['recommendation_status'], '•')
            
            return f"{template_name} - {user_name} {status_indicator}"
        except Exception:
            return "Categoría Sin Nombre"

    def update(self, data):
        """
        Actualiza los campos permitidos de la categoría
        """
        try:
            user_profile = data.get('user_profile')
            if not self.can_user_edit(user_profile):
                raise ValidationError("No tienes permisos para editar esta categoría")

            # Validar que no se intenten modificar campos readonly
            invalid_fields = set(data.keys()) & self.READONLY_FIELDS
            if invalid_fields:
                raise ValidationError(f"No se pueden modificar los campos: {', '.join(invalid_fields)}")

            # Actualizar solo campos editables
            for field, value in data.items():
                if field not in self.READONLY_FIELDS and hasattr(self, field):
                    setattr(self, field, value)
            
            self.save()
            return True
        except Exception as e:
            print(f"Error actualizando HealthCategory: {e}")
            raise ValidationError(str(e))

    def save_evaluation(self, responses=None):
        """Guarda o actualiza el formulario de evaluación"""
        if not hasattr(self, 'evaluation_form'):
            self.evaluation_form = EvaluationForm.objects.create(
                health_category=self,
                question_nodes=self.template.evaluation_form if self.template else {}
            )
        
        if responses is not None:
            if self.evaluation_form.responses is None:
                self.evaluation_form.responses = {}
            self.evaluation_form.responses.update(responses)
            self.evaluation_form.completed_date = timezone.now()
        
        self.evaluation_form.save()

    def save_recommendation(self, text, status_color, updated_by, is_draft=True):
        """
        Guarda o actualiza la recomendación
        
        Args:
            text (str): Texto de la recomendación
            status_color (str): Color del estado ('verde', 'amarillo', 'rojo', 'gris')
            updated_by (UserProfile): Usuario que realiza la actualización
            is_draft (bool): Si es un borrador o no
        """
        try:
            recommendation = self.get_or_create_recommendation()
            
            # Actualizar campos
            recommendation.text = text
            recommendation.status_color = status_color
            recommendation.updated_by = updated_by
            recommendation.is_draft = is_draft
            recommendation.updated_at = timezone.now()
            
            # Si no es borrador, marcar como firmado
            if not is_draft:
                recommendation.is_signed = True
                recommendation.signed_by = updated_by.get_full_name()
                recommendation.signed_at = timezone.now()
            
            recommendation.save()
            return True, "Recomendación guardada exitosamente"
            
        except Exception as e:
            return False, f"Error al guardar la recomendación: {str(e)}"

    def clear_evaluation(self):
        """
        Limpia el formulario de evaluación
        """
        self.evaluation_form.responses = {}
        self.evaluation_form.is_draft = True
        self.evaluation_form.completed_date = None
        self.evaluation_form.save()


    def clear_recommendation(self):
        """
        Limpia la recomendación
        """
        self.recommendation.text = ''
        self.recommendation.save()

    def get_status(self):
        try:
            return {
                'is_completed': self.evaluation_form.completed_date is not None,
                'recommendation_status': self.recommendation.status_color,
                'is_draft': self.recommendation.is_draft,
                'last_updated': self.recommendation.updated_at
            }
        except:
            return {
                'is_completed': False,
                'recommendation_status': 'gris',
                'is_draft': True,
                'last_updated': None
            }

    def can_user_edit(self, user_profile):
        """
        Verifica si un usuario puede editar esta instancia
        """
        if not user_profile:
            return False
            
        # Si el template está en modo readonly, nadie puede editar excepto admin
        if self.template.is_readonly and not user_profile.is_staff_member():
            return False
            
        # Verificar permisos en el template
        return self.template.can_user_edit(user_profile)

    def get_evaluation_data(self):
        """Obtiene los datos de evaluación"""
        try:
            return {
                'question_nodes': self.evaluation_form.question_nodes,
                'responses': self.evaluation_form.responses,
                'completed_date': self.evaluation_form.completed_date
            }
        except EvaluationForm.DoesNotExist:
            return None

    def get_recommendation_data(self):
        """Obtiene los datos de recomendación"""
        try:
            return {
                'text': self.recommendation.text,
                'status_color': self.recommendation.status_color,
                'updated_by': self.recommendation.updated_by,
                'updated_at': self.recommendation.updated_at,
                'is_draft': self.recommendation.is_draft
            }
        except Recommendation.DoesNotExist:
            return None

    def get_is_draft(self):
        """Helper method para obtener el estado de borrador de la recomendación"""
        try:
            return self.recommendation.is_draft
        except Recommendation.DoesNotExist:
            return True

    def get_or_create_recommendation(self):
        """
        Obtiene la recomendación existente o crea una nueva si no existe
        """
        try:
            return self.recommendation
        except Recommendation.DoesNotExist:
            return Recommendation.objects.create(
                health_category=self,
                status_color='gris',
                is_draft=True
            )

    def get_or_create_evaluation_form(self):
        """
        Obtiene el formulario de evaluación existente o crea uno nuevo si no existe
        """
        try:
            return self.evaluation_form
        except EvaluationForm.DoesNotExist:
            return EvaluationForm.objects.create(
                health_category=self,
                question_nodes=self.template.evaluation_form if self.template else {}
            )

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        
        if is_new:
            # Al crear una nueva instancia, agregar editores según el template
            from ..models import UserProfile
            editors = UserProfile.objects.filter(
                user__groups__name__in=self.template.allowed_editor_roles
            )
            self.editors.add(*editors)


 
    @property
    def recommendations(self):
        """
        Propiedad que retorna las recomendaciones o valores por defecto
        """
        try:
            recommendation = self.recommendation
            if not recommendation or not recommendation.text:
                return self.get_default_recommendation()
                
            return {
                "text": recommendation.text,
                "is_draft": recommendation.is_draft,
                "professional": recommendation.professional,
                "status": {
                    "color": recommendation.status_color,
                    "text": recommendation.get_status_display()
                },
                "updated_at": recommendation.updated_at.isoformat() if recommendation.updated_at else None
            }
        except Exception:
            return self.get_default_recommendation()
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