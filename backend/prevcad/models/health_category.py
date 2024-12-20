from typing import Any
from django.db import models
from django.utils.encoding import smart_str
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .activity_node import ActivityNode, ActivityNodeDescription
import base64


class CategoryTemplate(models.Model):
  icon = models.ImageField(upload_to='health_categories_icons/')
  name = models.TextField()
  description = models.TextField()
  is_active = models.BooleanField(default=True)
  evaluation_form = models.JSONField(
    null=True, 
    blank=True, 
    default=dict,
    help_text="Formulario de evaluación en formato JSON"
  )
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
    if self.icon:
      try:
        with self.icon.open('rb') as image_file:
          encoded_string = base64.b64encode(image_file.read())
          return encoded_string.decode('utf-8')
      except Exception as e:
        print(f"Error encoding image: {e}")
        return None
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
  
    super().save(*args, **kwargs)

  def update_evaluation_form(self, data):
    if not isinstance(data, dict):
      raise ValueError("Los datos deben ser un diccionario.")
      
    if "question_nodes" not in data:
      raise ValueError("Los datos deben contener 'question_nodes'.")
      
    if not isinstance(data["question_nodes"], list):
      raise ValueError("question_nodes debe ser una lista.")
      
    for node in data["question_nodes"]:
      if not isinstance(node, dict) or "type" not in node or "question" not in node:
        raise ValueError("Cada nodo debe ser un diccionario con 'type' y 'question'.")

    self.evaluation_form = data
    self.save(update_fields=['evaluation_form'])


  def update_training_form(self, data):
    if not isinstance(data, dict):
      raise ValueError("Los datos deben ser un diccionario.")

    if "training_nodes" not in data:
      raise ValueError("Los datos deben contener 'training_nodes'.")
    
    for node in data["training_nodes"]:
      if not isinstance(node, dict) or "type" not in node or "content" not in node:
        raise ValueError("Cada nodo debe ser un diccionario con 'type' y 'content'.")

    self.training_form = data
    self.save(update_fields=['training_form'])

  def __str__(self):
    return self.name


class HealthCategory(models.Model):
  COLOR_CHOICES = [
    ('green', 'Verde - Saludable'),
    ('yellow', 'Amarillo - Precaución'),
    ('red', 'Rojo - Atención Requerida'),
  ]

  user = models.ForeignKey(User, on_delete=models.CASCADE)
  template = models.ForeignKey(CategoryTemplate, on_delete=models.SET_NULL, null=True)
  responses = models.JSONField(null=True, blank=True)
  completion_date = models.DateTimeField(null=True, blank=True)
  status_color = models.CharField(
    max_length=10, 
    choices=COLOR_CHOICES,
    null=True, 
    blank=True,
    verbose_name="Estado de Salud"
  )
  doctor_recommendations = models.TextField(
    null=True, 
    blank=True,
    verbose_name="Recomendaciones del Doctor"
  )


  class Meta:
    verbose_name = "Categoría de Salud"
    verbose_name_plural = "Categorías de Salud"

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
    users = User.objects.all()
    for user in users:
      cls.objects.create(
        user=user,
        template=template,
      )


@receiver(post_save, sender=User)
def create_user_health_categories(sender, instance, created, **kwargs):
  """Crear categorías de salud para un nuevo usuario"""
  if created:
    # Obtener todos los templates activos
    templates = CategoryTemplate.objects.filter(is_active=True)
    
    # Crear una categoría por cada template para el nuevo usuario
    for template in templates:
      HealthCategory.objects.create(
        user=instance,
        template=template,
        evaluation_form=template.evaluation_form,
        training_form=template.training_form
      )


@receiver(post_save, sender=CategoryTemplate)
def create_health_categories_for_template(sender, instance, created, **kwargs):
  if created:
    HealthCategory.create_categories_for_template(instance)
