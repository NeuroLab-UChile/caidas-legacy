from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from .user_types import UserTypes





class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        blank=True,
        null=True
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text='Nombre de usuario para iniciar sesión'
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    role = models.CharField(
        max_length=50, 
        choices=UserTypes.choices,
        default=UserTypes.PATIENT,
        verbose_name="Tipo de Usuario"
    )
    specialty = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Especialidad del profesional (si aplica)"
    )
    profile_image = models.ImageField(
        upload_to='profile_images/',
        null=True,
        blank=True,
        verbose_name="Imagen de perfil"
    )

    @property
    def is_professional(self):
        """Verifica si el usuario es un profesional de la salud"""
        return UserTypes.is_professional(self.role)

    @property
    def is_staff_member(self):
        """Verifica si el usuario es personal administrativo"""
        return UserTypes.is_staff(self.role)

    def clean(self):
        super().clean()
        if User.objects.filter(username=self.username).exists() and (
            not self.user or self.user.username != self.username
        ):
            raise ValidationError({'username': 'Este nombre de usuario ya está en uso.'})

    @transaction.atomic
    def save(self, *args, **kwargs):
        creating = not self.pk
        if creating and not self.user:
            if User.objects.filter(username=self.username).exists():
                raise ValidationError({'username': 'Este nombre de usuario ya está en uso.'})
            
            try:
                user = User.objects.create(
                    username=self.username,
                    email=self.email,
                    first_name=self.first_name or '',
                    last_name=self.last_name or ''
                )
                
                if self.role == 'admin':
                    user.is_staff = True
                    user.is_superuser = True
                elif self.role == 'doctor':
                    user.is_staff = True
                
                temp_password = str(uuid.uuid4())
                user.set_password(temp_password)
                user.save()
                
                self.user = user
                
            except Exception as e:
                raise ValidationError(f'Error al crear el usuario: {str(e)}')
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"

    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'





    def __str__(self):
        return f"{self.username} - {self.get_role_display()}" 


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

    def delete(self, *args, **kwargs):
        # Eliminar la imagen al eliminar el perfil
        if self.profile_image:
            self.profile_image.delete()
        super().delete(*args, **kwargs) 
