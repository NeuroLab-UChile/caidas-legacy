from typing import Any
from django.db import models
from django.utils.encoding import smart_str
from django.contrib.auth.models import User

class HealthCategory(models.Model):

  class CategoryType(models.TextChoices):
    PHYSICAL_ACTIVITY = 'PHYSICAL_ACTIVITY', 'Physical Activity'
    NUTRITION = 'NUTRITION', 'Nutrition'
    MENTAL_HEALTH = 'MENTAL_HEALTH', 'Mental Health'
    SLEEP = 'SLEEP', 'Sleep'
    HYDRATION = 'HYDRATION', 'Hydration'
    STRESS = 'STRESS', 'Stress'
    SOCIAL_CONNECTION = 'SOCIAL_CONNECTION', 'Social Connection'
    SUBSTANCE_USE = 'SUBSTANCE_USE', 'Substance Use'
    SEXUAL_HEALTH = 'SEXUAL_HEALTH', 'Sexual Health'
    SAFETY = 'SAFETY', 'Safety'
    GENERAL_HEALTH = 'GENERAL_HEALTH', 'General Health'

  icon = models.ImageField(upload_to='health_categories_icons/')
  name = models.CharField(max_length=100)
  description = models.TextField(max_length=10000)
  description_2 = models.TextField( null=True, blank=True)
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  type = models.CharField(max_length=100, choices=CategoryType.choices)
  evaluation_form = models.JSONField(null=True, blank=True)
  workout_form = models.JSONField(null=True, blank=True)
  category_form = models.JSONField(null=True, blank=True)
  






