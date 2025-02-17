from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    """
    Modelo de usuario personalizado que extiende AbstractUser
    """
    email = models.EmailField(_('email address'), unique=True)
    
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user should be treated as active.')
    )
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.username

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def save(self, *args, **kwargs):
        """
        Override del método save para asegurar que el email sea único
        """
        self.email = self.email.lower()  # Normalizar email
        super().save(*args, **kwargs)

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal para crear o actualizar el perfil del usuario automáticamente
    """
    from .user_profile import UserProfile
    
    if created:
        # Crear nuevo perfil
        UserProfile.objects.create(user=instance)
    else:
        # Asegurar que existe el perfil
        UserProfile.objects.get_or_create(user=instance)
