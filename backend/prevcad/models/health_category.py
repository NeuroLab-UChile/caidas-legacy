from typing import Any
from django.db import models
from django.utils.encoding import smart_str

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from .activity_node import ActivityNode, ActivityNodeDescription
import base64
import os
from django.conf import settings
from .user_profile import UserProfile
from django.utils.translation import gettext_lazy as _


class CategoryTemplate(models.Model):
  icon = models.ImageField(
    upload_to='health_categories_icons',
    null=True,
    blank=True
  )
  name = models.TextField()
  description = models.TextField()
  is_active = models.BooleanField(default=True)
  EVALUATION_TYPE_CHOICES = [
    ('SELF', 'Autoevaluación'),
    ('PROFESSIONAL', 'Evaluación Profesional'),
    ('BOTH', 'Ambas Evaluaciones')
  ]
  evaluation_type = models.CharField(
    max_length=20,
    choices=EVALUATION_TYPE_CHOICES,
    default='SELF',
    verbose_name="Tipo de Evaluación",
    help_text="Define quién puede realizar la evaluación"
  )
  # Formulario para autoevaluación
  self_evaluation_form = models.JSONField(
    null=True,
    blank=True,
    default=dict,
    help_text="Formulario de autoevaluación en formato JSON"
  )
  # Formulario para evaluación profesional
  professional_evaluation_form = models.JSONField(
    null=True,
    blank=True,
    default=dict,
    help_text="Formulario de evaluación profesional en formato JSON"
  )

  # Agregar el campo training_form
  training_form = models.JSONField(
    null=True,
    blank=True,
    default=dict,
    help_text="Formulario de entrenamiento en formato JSON"
  )
  root_node = models.OneToOneField(
    ActivityNodeDescription,
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    related_name="category_template",
    verbose_name="Nodo raíz"
  )

  def get_icon_base64(self):
    try:
      if not self.icon:
        return None
        
      # Construir la ruta correcta usando MEDIA_ROOT
      relative_path = str(self.icon).lstrip('/')  # Eliminar slash inicial si existe
      icon_path = os.path.join(settings.MEDIA_ROOT, relative_path)
      
      print(f"Debug - Icon paths:")
      print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
      print(f"Relative path: {relative_path}")
      print(f"Full path: {icon_path}")
      
      # Verificar que el archivo existe
      if not os.path.exists(icon_path):
        print(f"Icon file not found at: {icon_path}")
        return None
        
      # Leer y codificar el archivo
      with open(icon_path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
      # Determinar el tipo MIME
      extension = os.path.splitext(icon_path)[1].lower()
      mime_type = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif'
      }.get(extension, 'image/png')
        
      return f"data:{mime_type};base64,{encoded_string}"
      
    except Exception as e:
      print(f"Error encoding image: {str(e)}")
      print(f"Icon type: {type(self.icon)}")
      print(f"Icon value: {self.icon}")
      return None
  def get_ordered_training_nodes(self):
    """Retorna los nodos de entrenamiento ordenados"""
    if not self.training_form:
      return []
      
    nodes = self.training_form['training_nodes']  
    for i, node in enumerate(nodes):
      node['next_node_id'] = nodes[i + 1]['id'] if i < len(nodes) - 1 else None

    return nodes

  def save(self, *args, **kwargs):
    if not self.root_node:
      # Crear el nodo raíz usando ActivityNodeDescription en lugar de ActivityNode
      self.root_node = ActivityNodeDescription.objects.create(
        type=ActivityNodeDescription.NodeType.CATEGORY_DESCRIPTION,
        description=self.description
      )
  
    # Si el icono tiene una ruta con slash inicial, corregirlo
    if self.icon and isinstance(self.icon, str) and self.icon.startswith('/'):
      self.icon = self.icon.lstrip('/')
    super().save(*args, **kwargs)

  def get_evaluation_form(self):
    """Retorna el formulario de evaluación apropiado según el tipo"""
    if self.evaluation_type == 'SELF':
      return self.self_evaluation_form
    elif self.evaluation_type == 'PROFESSIONAL':
      return self.professional_evaluation_form
    return None

  def get_evaluation_results(self):
    """Retorna los resultados de evaluación apropiados según el tipo"""
    if self.evaluation_type == 'SELF':
      return self.self_evaluation_results
    elif self.evaluation_type == 'PROFESSIONAL':
      return self.professional_evaluation_result
    return None

  def update_evaluation_form(self, data):
    """Actualiza el formulario de evaluación apropiado según el tipo"""
    if self.evaluation_type == 'SELF':
      self.update_self_evaluation_form(data)
    elif self.evaluation_type == 'PROFESSIONAL':
      self.update_professional_evaluation_form(data)

  def update_self_evaluation_form(self, data):
    if not isinstance(data, dict):
      raise ValueError("Los datos deben ser un diccionario.")
      
    if "question_nodes" not in data:
      raise ValueError("Los datos deben contener 'question_nodes'.")
      
    for node in data["question_nodes"]:
      if not isinstance(node, dict) or "type" not in node or "question" not in node:
        raise ValueError("Cada nodo debe ser un diccionario con 'type' y 'question'.")

    self.self_evaluation_form = data
    self.save(update_fields=['self_evaluation_form'])

  def update_professional_evaluation_form(self, data):
    if not isinstance(data, dict):
      raise ValueError("Los datos deben ser un diccionario.")
      
    if "evaluation_sections" not in data:
      raise ValueError("Los datos deben contener 'evaluation_sections'.")
      
    for section in data["evaluation_sections"]:
      if not isinstance(section, dict) or "title" not in section or "fields" not in section:
        raise ValueError("Cada sección debe tener 'title' y 'fields'.")

    self.professional_evaluation_form = data
    self.save(update_fields=['professional_evaluation_form'])

  def can_self_evaluate(self):
    return self.evaluation_type in ['SELF', 'BOTH']

  def can_professional_evaluate(self):
    return self.evaluation_type in ['PROFESSIONAL', 'BOTH']

  def __str__(self):
    return self.name


class HealthCategory(models.Model):
    STATUS_CHOICES = [
        ('borrador', 'Borrador'),
        ('publicado', 'Publicado'),
        ('archivado', 'Archivado')
    ]

    COLOR_CHOICES = [
        ('verde', 'Verde'),
        ('amarillo', 'Amarillo'),
        ('rojo', 'Rojo'),
        ('gris', 'Gris'),
    ]

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name="Usuario")
    template = models.ForeignKey(CategoryTemplate, on_delete=models.CASCADE, verbose_name="Plantilla")
    completion_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de completado")
    responses = models.JSONField(null=True, blank=True, verbose_name="Respuestas")
    professional_recommendations = models.TextField(null=True, blank=True, verbose_name="Recomendaciones médicas")
    professional_recommendations_updated_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de actualización")
    professional_recommendations_updated_by = models.CharField(max_length=150, blank=True, null=True, verbose_name="Actualizado por")
    status_color = models.CharField(
        max_length=20,
        choices=COLOR_CHOICES,
        null=True,
        blank=True,
        verbose_name="Color de riesgo"
    )
    is_draft = models.BooleanField(
        default=True,
        verbose_name="Es borrador",
        help_text="Si está marcado, las recomendaciones no serán visibles para el paciente"
    )
    evaluation_form = models.JSONField(null=True, blank=True, verbose_name="Formulario de evaluación")
    # Resultados de la autoevaluación
    self_evaluation_results = models.JSONField(
        null=True,
        blank=True,
        default=dict,
        help_text="Resultados de la autoevaluación del paciente"
    )
    # Resultados de la evaluación profesional

    professional_evaluation_data = models.JSONField(default=dict, blank=True)
    professional_evaluation_result = models.TextField(
        blank=True, 
        null=True,
        verbose_name='Resultado de Evaluación Profesional',
        help_text='Complete este campo solo para evaluaciones profesionales.'
    )

    class Meta:
        verbose_name = "Categoría de Salud"
        verbose_name_plural = "Categorías de Salud"
        ordering = ['-completion_date']

    @classmethod
    def create_categories_for_user(cls, user):
        templates = CategoryTemplate.objects.filter(is_active=True)
        for template in templates:
            cls.objects.create(
                user=user,
                template=template,
            )

    @classmethod
    def create_categories_for_template(cls, template):
        users = UserProfile.objects.all()
        for user in users:
            cls.objects.create(
                user=user,
                template=template,
              )

    def can_edit_recommendations(self, user_profile):
        """
        Verifica si un usuario puede editar las recomendaciones
        basado en su rol.
        """
        ALLOWED_ROLES = ['doctor', 'admin']  # Roles permitidos
        return user_profile.role in ALLOWED_ROLES

    def save(self, *args, **kwargs):
        updated_by = kwargs.pop('updated_by', None)
        
        if self.pk:
            old_instance = HealthCategory.objects.get(pk=self.pk)
            if (old_instance.professional_recommendations != self.professional_recommendations or 
                old_instance.is_draft != self.is_draft):
                
                # Solo actualizar si el usuario tiene permisos
                if updated_by and hasattr(updated_by, 'profile'):
                    if self.can_edit_recommendations(updated_by.profile):
                        self.professional_recommendations_updated_at = timezone.now()
                        self.professional_recommendations_updated_by = (
                            updated_by.get_full_name() or updated_by.username
                        )
                    else:
                        raise PermissionError("No tienes permisos para editar recomendaciones")

        super().save(*args, **kwargs)

    def can_self_evaluate(self):
        return self.template.can_self_evaluate()

    def can_professional_evaluate(self):
        return self.template.can_professional_evaluate()

    def get_evaluation_results(self):
        """Retorna los resultados de evaluación apropiados según el tipo de template"""
        if self.template.evaluation_type == 'SELF':
            return self.self_evaluation_results
        elif self.template.evaluation_type == 'PROFESSIONAL':
            return self.professional_evaluation_result
        return None

    def update_evaluation_results(self, data, user=None):
        """Actualiza los resultados de evaluación según el tipo"""
        if self.template.evaluation_type == 'SELF':
            self.update_self_evaluation(user, data)
        elif self.template.evaluation_type == 'PROFESSIONAL':
            self.update_professional_evaluation(user, data)

    def update_self_evaluation(self, user, evaluation_data):
        if not self.template.can_self_evaluate():
            raise ValueError("Esta categoría no permite autoevaluación")

        self.self_evaluation_results = {
            "date": timezone.now().isoformat(),
            "user_id": user.id,
            "evaluation_data": evaluation_data,
            "updated_at": timezone.now().isoformat()
        }
        self.save(update_fields=['self_evaluation_results'])

    def update_professional_evaluation(self, professional_user, evaluation_data):
        if not self.template.can_professional_evaluate():
            raise ValueError("Esta categoría no permite evaluación profesional")
        if not professional_user.is_professional:
            raise ValueError("Solo los profesionales pueden actualizar la evaluación")

        self.professional_evaluation_result = {
            "date": timezone.now().isoformat(),
            "professional_id": professional_user.id,
            "professional_name": professional_user.get_full_name(),
            "evaluation_data": evaluation_data,
            "updated_at": timezone.now().isoformat()
        }
        self.save(update_fields=['professional_evaluation_result'])





@receiver(post_save, sender=UserProfile)
def create_user_health_categories(sender, instance, created, **kwargs):
    """Crear categorías de salud para un nuevo usuario"""
    if created:
        # Obtener todos los templates activos
        templates = CategoryTemplate.objects.filter(is_active=True)
        
        # Crear una categoría por cada template para el nuevo usuario
        for template in templates:
            defaults = {
                'user': instance,
                'template': template,
            }
            
            # Agregar los formularios según el tipo de evaluación
            if template.evaluation_type == 'SELF':
                defaults['self_evaluation_results'] = {}
            elif template.evaluation_type == 'PROFESSIONAL':
                defaults['professional_evaluation_result'] = {}
            
            HealthCategory.objects.create(**defaults)


@receiver(post_save, sender=CategoryTemplate)
def create_health_categories_for_template(sender, instance, created, **kwargs):
    """Crear categorías de salud cuando se crea un nuevo template"""
    if created:
        # Obtener todos los usuarios
        users = UserProfile.objects.all()
        
        # Crear una categoría para cada usuario
        for user in users:
            defaults = {
                'user': user,
                'template': instance,
            }
            
            # Agregar los formularios según el tipo de evaluación
            if instance.evaluation_type == 'SELF':
                defaults['self_evaluation_results'] = {}
            elif instance.evaluation_type == 'PROFESSIONAL':
                defaults['professional_evaluation_result'] = {}
            
            HealthCategory.objects.create(**defaults)


@receiver(pre_delete, sender=CategoryTemplate)
def delete_related_health_categories(sender, instance, **kwargs):
    """Eliminar todas las categorías de salud asociadas cuando se elimina un template"""
    HealthCategory.objects.filter(template=instance).delete()
