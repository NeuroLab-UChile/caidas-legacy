from typing import Any
from django.db import models
from django.utils.encoding import smart_str
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .activity import ActivityNode, ActivityNodeDescription

# The admin creates this instance
class CategoryTemplate(models.Model):
    """Template for health categories that will be created for each user"""
    icon = models.ImageField(upload_to='health_categories_icons/')
    name = models.TextField()
    description = models.TextField()  # Se mantiene para crear el root node
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)

            # Crear el nodo raíz basado en la descripción de la plantilla
            root_node = ActivityNodeDescription.objects.create(
                type=ActivityNode.NodeType.CATEGORY_DESCRIPTION,
                description=self.description  # Usamos la descripción aquí
            )

            # Crear las categorías de salud para cada usuario
            for user in User.objects.all():
                HealthCategory.objects.create(
                    user=user,
                    template=self,
                    root_node=root_node  # Asociamos el nodo raíz
                )
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class HealthCategory(models.Model):
    """User-specific instance of a health category"""
    template = models.ForeignKey(CategoryTemplate, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_categories')
    root_node = models.ForeignKey('ActivityNodeDescription', on_delete=models.SET_NULL, null=True, blank=True, related_name='health_categories')

    @classmethod
    def create_categories_for_user(cls, user):
        """Creates health categories for a user based on active templates"""
        templates = CategoryTemplate.objects.filter(is_active=True)

        for template in templates:
            # Crear el nodo raíz (se asocia a la descripción de la plantilla)
            root_node = ActivityNodeDescription.objects.create(
                type=ActivityNode.NodeType.CATEGORY_DESCRIPTION,
                description=template.description
            )

            # Crear la categoría de salud para el usuario
            cls.objects.create(
                user=user,
                template=template,
                root_node=root_node
            )

@receiver(post_save, sender=User)
def create_user_health_categories(sender, instance, created, **kwargs):
  if created:
    HealthCategory.create_categories_for_user(instance)
