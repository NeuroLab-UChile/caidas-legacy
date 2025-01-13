from django.db import models
from .activity_node import ActivityNodeDescription
import base64
import os
from django.conf import settings
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .user_types import UserTypes
from django.core.exceptions import ValidationError

class CategoryTemplate(models.Model):
  """
  Template for health categories
  """
  # Basic information
  name = models.CharField(max_length=200)
  icon = models.ImageField(
    upload_to='health_categories_icons',
    null=True,
    blank=True
  )

  description = models.TextField(blank=True)
  is_active = models.BooleanField(default=True)

  # Evaluation 
  evaluation_type = models.CharField(
    max_length=20,
    choices=[
       ('SELF', 'Autoevaluación'),
       ('PROFESSIONAL', 'Evaluación Profesional'),
       ('BOTH', 'Ambas Evaluaciones')
    ],
    default='SELF',
    verbose_name="Tipo de Evaluación",
    help_text="Define quién puede realizar la evaluación"
    
  )
  evaluation_form = models.JSONField(
    null=True,
    blank=True,
    default=dict,
    help_text="Formulario de autoevaluación en formato JSON"
  )
  # Formulario para evaluación profesional

  default_recommendations = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        help_text='Recomendaciones predeterminadas según el color de estado'
    )
  
  training_form = models.JSONField(
    null=True,
    blank=True,
    default=dict,
    help_text="Formulario de entrenamiento en formato JSON"
  )

  # Agregar el campo training_form

  root_node = models.OneToOneField(
    ActivityNodeDescription,
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    related_name="category_template",
    verbose_name="Nodo raíz"
  )

  # Simplificar a un solo campo para roles con permiso de edición
  allowed_editor_roles = models.JSONField(
        default=list,
        help_text="Roles que pueden editar instancias basadas en este template",
        verbose_name="Roles con permiso de edición"
    )

  # Nuevo campo para control global de solo lectura
  is_readonly = models.BooleanField(
        default=False,
        help_text="Si está activo, todas las instancias serán de solo lectura independientemente de los roles",
        verbose_name="Solo lectura global"
    )

  evaluation_tags = models.JSONField(
        default=list,
        help_text="Etiquetas para la evaluación",
        verbose_name="Etiquetas de evaluación"
    )

  @property
  def available_roles(self):
        """Retorna lista de choices para roles disponibles"""
        return [(role.value, role.label) for role in UserTypes]
  def get_default_recommendation(self):
    return self.default_recommendations
  def clean(self):
        """Valida que los roles seleccionados sean válidos"""
        super().clean()
        if self.allowed_editor_roles:
            valid_roles = [role.value for role in UserTypes]
            invalid_roles = [role for role in self.allowed_editor_roles if role not in valid_roles]
            if invalid_roles:
                raise ValidationError({
                    'allowed_editor_roles': f'Roles inválidos: {", ".join(invalid_roles)}'
                })

  def can_user_edit(self, user_profile):
        """
        Verifica si un usuario puede editar instancias basadas en este template
        """
        if not user_profile or self.is_readonly:
            return False
            
        # Admins siempre pueden editar
        if user_profile.is_staff_member():
            return True
            
        return user_profile.role in self.allowed_editor_roles

  def update_instance_editors(self):
        """
        Actualiza los editores en todas las instancias de HealthCategory
        basadas en este template
        """
        from .health_category import HealthCategory
        
        # Obtener todas las instancias relacionadas
        instances = HealthCategory.objects.filter(template=self)
        
        for instance in instances:
            # Limpiar editores existentes
            instance.editors.clear()
            
            # Agregar nuevos editores basados en roles permitidos
            from ..models import UserProfile
            editors = UserProfile.objects.filter(
                user__groups__name__in=self.allowed_editor_roles
            )
            instance.editors.add(*editors)

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
    is_new = self.pk is None
    super().save(*args, **kwargs)
    
    if not is_new:
        # Actualizar editores en instancias existentes
        self.update_instance_editors()

  def can_self_evaluate(self):
    return self.evaluation_type in ['SELF', 'BOTH']

  def can_professional_evaluate(self):
    return self.evaluation_type in ['PROFESSIONAL', 'BOTH']

  def __str__(self):
    return self.name

  def can_edit(self, user):
    """
    Verifica si un usuario puede editar esta plantilla
    """
    if user.is_superuser:
      return True
            
    # Verificar si el usuario pertenece a algún grupo con permiso
    return user.groups.filter(id__in=self.editable_by_groups.all()).exists()

  def get_question_nodes(self):
    """Obtener los nodos de preguntas según el tipo de evaluación"""
    print(f"Obteniendo nodos para template: {self.name}")  # Debug
    
    if self.evaluation_type == 'PROFESSIONAL':
      nodes = [
        {
          'id': 'observations',
          'type': 'text',
          'label': 'Observaciones',
          'required': True
        },
        {
          'id': 'diagnosis',
          'type': 'text',
          'label': 'Diagnóstico',
          'required': True
        }
      ]
      print("Nodos profesionales:", nodes)  # Debug
      return nodes
      
    # Para autoevaluación
    return self.evaluation_form.get('question_nodes', [])
  

class CategoryTemplateEditor(models.Model):
    """Modelo intermedio para manejar permisos de edición de templates"""
    template = models.ForeignKey(CategoryTemplate, on_delete=models.CASCADE)
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    editable_fields = models.JSONField(
        default=list,
        help_text="Lista de campos que el usuario puede editar"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['template', 'user']




