from typing import Any
from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

  def save(self, *args: Any, **kwargs: Any) -> None:
    super().save(*args, **kwargs)

  def __str__(self):
    return self.user.username
