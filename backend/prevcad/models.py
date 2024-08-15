from typing import Any
from django.db import models

class Card(models.Model):
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=100)
  image = models.CharField(max_length=500)
  description = models.TextField(max_length=10000)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  class Meta:
    abstract = True


class HealthCategory(Card):
  icon = models.CharField(max_length=500)
  
  class Meta:
    db_table = 'health_categories'


class HealthRecommendation(Card):
  health_category = models.ForeignKey('HealthCategory', on_delete=models.CASCADE)
  result = models.TextField()
  view_info = models.TextField()
  
  class Meta:
    abstract = True



class WorkRecommendation(HealthRecommendation):
  health_category = models.ForeignKey('HealthCategory', related_name='work_recommendations', on_delete=models.CASCADE)
  work_specific_field = models.CharField(max_length=100)
  
  class Meta:
    db_table = 'work_recommendations'


class EvaluationRecommendation(HealthRecommendation):
  health_category = models.ForeignKey('HealthCategory', related_name='evaluation_recommendations', on_delete=models.CASCADE)
  evaluation_specific_field = models.CharField(max_length=100)
  
  class Meta:
    db_table = 'evaluation_recommendations'


class TextRecomendation(models.Model):
  id = models.BigAutoField(primary_key=True)
  title = models.CharField(max_length=100)
  inside_text = models.CharField(max_length=200)

  class Meta:
      db_table = 'text_recomendation'