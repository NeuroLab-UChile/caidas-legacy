from typing import Any
from django.db import models
from django.utils.encoding import smart_str


class Card(models.Model):
  name = models.CharField(max_length=100)
  image = models.ImageField(name='image', upload_to='health_categories_images/')
  description = models.TextField(max_length=10000)

  def save(self, *args: Any, **kwargs: Any) -> None:
    self.name = smart_str(self.name)
    self.description = smart_str(self.description)
    super().save(*args, **kwargs)

  def upload_to(self, instance: Any, filename: str) -> str:
    return f'{instance.__class__.__name__}/{filename}'

  def __str__(self):
    return self.name

  class Meta:
    abstract = True


class HealthCategory(Card):
  icon = models.ImageField(upload_to='health_categories_icons/')

  def save(self, *args: Any, **kwargs: Any) -> None:
    super().save(*args, **kwargs)

  class Meta:
    db_table = 'health_categories'
