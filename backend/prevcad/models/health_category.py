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
  description = models.TextField()
  is_active = models.BooleanField(default=True)

  def save(self, *args, **kwargs):
    if not self.pk:
      super().save(*args, **kwargs)

      root_node = ActivityNodeDescription.objects.create(
        type=ActivityNode.NodeType.CATEGORY_DESCRIPTION,
        description=self.description
      )

      for user in User.objects.all():
        HealthCategory.objects.create(
          user=user,
          template=self,
          root_node_id=root_node.id
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

  def __str__(self):
    return f"{self.template.name} - {self.user.username}"

  @classmethod
  def create_categories_for_user(cls, user):
    """Creates health categories for a user based on active templates"""
    templates = CategoryTemplate.objects.filter(is_active=True)

    for template in templates:
      root_node = ActivityNodeDescription.objects.create(
        type=ActivityNode.NodeType.CATEGORY_DESCRIPTION,
        description=template.description
      )

      cls.objects.create(
        user=user,
        template=template,
        root_node=root_node
      )

@receiver(post_save, sender=User)
def create_user_health_categories(sender, instance, created, **kwargs):
  if created:
    HealthCategory.create_categories_for_user(instance)
