from typing import Any
from django.db import models
from django.utils.encoding import smart_str
from django.contrib.auth.models import User

class PhysicalActivity(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  name = models.CharField(max_length=100)
  image = models.ImageField(name='image', upload_to='health_categories')
  description = models.TextField(max_length=10000)
  description_2 = models.TextField(max_length=10000)

  def save(self, *args: Any, **kwargs: Any) -> None:
    self.name = smart_str(self.name)
    self.description = smart_str(self.description)
    super().save(*args, **kwargs)

  def __str__(self):
    return self.name
