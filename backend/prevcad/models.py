from typing import Any
from django.db import models
    
class Card(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    image = models.TextField(max_length=100)
    description = models.TextField(max_length=10000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:

        abstract = True

class HealthCategory(Card):
    icon = models.TextField(max_length=100) # Image


    class Meta:
        db_table = 'health_categories'

    def get_evaluation(self) -> str:
        return self.name
    
    def create_health_recomendation(self, user):
        return self.recomendations.create(user=user)
    
    def delete_health_recomendation(self, card_id):
        return self.recomendations.get(id=card_id).delete()
    
    def get_health_recomendation(self, card_id):
        return self.objects.get(id=card_id)
    
    def get_health_recomendation_all(self):
        return self.objects.all()
    
    def get_user_health_recomendation_all(self, user_id):
        return self.objects.filter(user=user_id)
    
    def update_health_recomendation(self, card_id):
        card = self.objects.get(id=card_id)
        card.save()

class HealthRecomedation(Card):
    result = models.TextField()
    view_info = models.TextField()


    class Meta:
        db_table = 'health_recomendations'
        abstract = True
    
    def get_result(self):
        return self.result
    
    def get_view_info(self):
        return self.view_info
    
class WorkRecomendation(HealthRecomedation):
    
    class Meta:
        db_table = 'work_recomendations'
      
    
    def get_result(self):
        super().get_result()

class EvaluationRecomendation(HealthRecomedation):

    class Meta:
        db_table = 'evaluation_recomendations'
    
    def get_result(self):
        super().get_result()