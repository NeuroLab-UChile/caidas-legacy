from django.db import models



class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username
    
    class Meta:
        db_table = 'users'
        ordering = ['created_at']


class Admin(User):
    class Meta:
        db_table = 'admins'
    def create_user(self, username, email, password):
        return User.objects.create(username=username, email=email, password=password)
    def delete_user(self, user_id):
        return User.objects.get(id=user_id).delete()
    
class Customer(User):
    class Meta:
        db_table = 'customers'
    
    def get_health_category(self):
        return self.health_category
    
    def post_nosequewea(self):
        return self.nosequewea
    
    


class health_recomendation(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(max_length=100)
    image = models.TextField(max_length=100)
    description = models.TextField(max_length=10000)
 
    
    def __str__(self):
        return self.card_number
    
    class Meta:
        db_table = 'cards'
        ordering = ['created_at']
        abstract = True
    

class Card(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    image = models.TextField(max_length=100)
    description = models.TextField(max_length=10000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    class Meta:
        db_table = 'cards'
        abstract = True
    

class HealthCategory(Card):
    icon = models.TextField(max_length=100) # Image

    class Meta:
        db_table = 'health_categories'


    def get_evaluation(self) -> str:
        return self.name
    
    def create_health_recomendation(self, user):
        return self.objects.create(user=user)
    
    def delete_health_recomendation(self, card_id):
        return Card.objects.get(id=card_id).delete()
    
    def get_health_recomendation(self, card_id):
        return Card.objects.get(id=card_id)
    
    def get_health_recomendation_all(self):
        return Card.objects.all()
    
    def get_user_health_recomendation_all(self, user_id):
        return Card.objects.filter(user=user_id)
    
    def update_health_recomendation(self, card_id):
        card = Card.objects.get(id=card_id)
        card.save()

    
    
class HealthRecomedation(Card):
    result = models.TextField()
    view_info = models.TextField()


    
    class Meta:
        db_table = 'health_recomendations'
    
    def get_result(self):
        return self.result
    
    def get_view_info(self):
        return self.view_info


class WorkRecomendation(Card):
    result = models.TextField()
    
    class Meta:
        db_table = 'work_recomendations'
    
    def get_result(self):
        super().get_result()

class EvaluationRecomendation(Card):
    result = models.TextField()
    
    class Meta:
        db_table = 'evaluation_recomendations'
    
    def get_result(self):
        super().get_result()


   
      
    
    
