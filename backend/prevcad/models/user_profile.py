from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    profile_image = models.ImageField(
        upload_to='profile_images/',
        null=True,
        blank=True
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        default=''
    )
    birth_date = models.DateField(
        null=True,
        blank=True
    )
    # ... otros campos que quieras agregar ...

    def __str__(self):
        return f"Perfil de {self.user.username}"

    class Meta:
        db_table = 'user_profile'

# Señal para crear automáticamente el perfil
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# Señal para guardar el perfil
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)
    instance.profile.save() 