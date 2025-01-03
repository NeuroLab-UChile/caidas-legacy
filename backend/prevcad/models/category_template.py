from django.db import models
from .activity_node import ActivityNodeDescription
import base64
import os
from django.conf import settings

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

  editable_fields_by_user_type = models.JSONField(
        default=dict,
        help_text="Defina los campos editables para cada tipo de usuario. Ejemplo: {'DOCTOR': ['recommendations', 'status_color'], 'NURSE': ['recommendations']}",
    )

  # Agregar campo para grupos con permisos de edición
  editable_by_groups = models.ManyToManyField(
    'auth.Group',
    related_name='editable_templates',
    blank=True,
    verbose_name="Grupos que pueden editar",
    help_text="Selecciona los grupos que pueden editar esta plantilla"
  )

  def can_user_edit(self, user_profile, field=None):
        """
        Verifica si un usuario puede editar este template o un campo específico según el rol
        y los campos definidos en editable_fields_by_user_type.
        """
        if not user_profile:
            return False

        if user_profile.role == UserTypes.ADMIN:
            return True  # Administradores pueden editar todo

        editable_fields = self.editable_fields_by_user_type.get(user_profile.role, [])
        if field:
            return field in editable_fields
        return bool(editable_fields)
  
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




