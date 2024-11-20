from typing import Any
from django.db import models
from django.utils.encoding import smart_str
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class CategoryTemplate(models.Model):
    """Template for health categories that will be created for each user"""
    icon = models.ImageField(upload_to='health_categories_icons/')
    name = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Health Category Template"
        verbose_name_plural = "Health Category Templates"

class HealthCategory(models.Model):
    """User-specific instance of a health category"""
    template = models.ForeignKey(CategoryTemplate, on_delete=models.SET_NULL, null=True)
    icon = models.ImageField(upload_to='health_categories_icons/')
    name = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_categories')
    root_node_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"

    @classmethod
    def create_categories_for_user(cls, user):
        """Creates health categories for a user based on active templates"""
        templates = CategoryTemplate.objects.filter(is_active=True)

        for template in templates:
            cls.objects.create(
                user=user,
                template=template,
                name=template.name,
                icon=template.icon
            )

@receiver(post_save, sender=User)
def create_user_health_categories(sender, instance, created, **kwargs):
    if created:
        HealthCategory.create_categories_for_user(instance)

# Your existing ActivityNode classes remain unchanged
class ActivityNode(models.Model):
    class NodeType(models.TextChoices):
        CATEGORY_DESCRIPTION = 'CATEGORY_DESCRIPTION', 'Category Description'

    type = models.TextField(choices=NodeType.choices)

    class Meta:
        abstract = True

class ActivityNodeDescription(ActivityNode):
    description = models.TextField()
    first_button_text = models.TextField(null=True, blank=True)
    second_button_text = models.TextField(null=True, blank=True)
    first_button_node_id = models.IntegerField(null=True, blank=True)
    second_button_node_id = models.IntegerField(null=True, blank=True)

class ActivityNodeQuestion(ActivityNode):
    prev_node_id = models.IntegerField(null=True, blank=True)
    next_node_id = models.IntegerField(null=True, blank=True)
    question = models.TextField()
    options = models.JSONField()
    response = models.JSONField()

    class Meta:
        abstract = True

class TextQuestion(ActivityNodeQuestion):
    pass

class SingleChoiceQuestion(ActivityNodeQuestion):
    pass

class MultipleChoiceQuestion(ActivityNodeQuestion):
    pass

class ScaleQuestion(ActivityNodeQuestion):
    pass

class ImageQuestion(ActivityNodeQuestion):
    pass


