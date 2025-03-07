from django.conf import settings
from django.db import models
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import transaction
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from .user_types import UserTypes
from prevcad.utils import build_media_url


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    profile_image = models.ImageField(
        'Foto de perfil',
        upload_to='profile_images/',  # Ruta simple
        null=True,
        blank=True
    )
    phone = models.CharField(
        'Teléfono',
        max_length=20,
        null=True,
        blank=True
    )
    birth_date = models.DateField(
        'Fecha de nacimiento',
        null=True,
        blank=True
    )
    specialty = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Especialidad del profesional (si aplica)"
    )

    @property
    def role(self):
        """Obtiene el rol del usuario basado en su grupo"""
        group = self.user.groups.first()
        return group.name if group else None

    @property
    def role_label(self):
        """Obtiene la etiqueta amigable del rol del usuario"""
        role = self.role
        if not role:
            return "Sin rol"
        try:
            return UserTypes(role).label
        except ValueError:
            return role

    def is_professional(self):
        """Verifica si el usuario es un profesional de la salud"""
        return UserTypes.is_professional(self.role)

    def is_staff_member(self):
        """Verifica si el usuario es personal administrativo"""
        return UserTypes.is_staff(self.role)

    def save(self, *args, **kwargs):
        """
        Override del método save para manejar la creación inicial
        """
        creating = not self.pk
        super().save(*args, **kwargs)
        
        if creating and not self.user.groups.exists():
            # Asignar rol por defecto
            default_group, _ = Group.objects.get_or_create(name=UserTypes.PATIENT.value)
            self.user.groups.add(default_group)

    def get_roles(self):
        """
        Retorna lista de roles del usuario con sus etiquetas.
        """
        if not self.role:
            return []
            
        roles = []
        if ',' in self.role:
            role_values = [role.strip().upper() for role in self.role.split(',')]
        elif '_' in self.role:
            role_values = [role.strip().upper() for role in self.role.split('_')]
        else:
            role_values = [self.role.upper()]
            
        for role_value in role_values:
            try:
                roles.append({
                    'value': role_value,
                    'label': UserTypes(role_value).label
                })
            except ValueError:
                roles.append({
                    'value': role_value,
                    'label': role_value
                })
                
        return roles

    def has_role(self, role):
        """
        Verifica si el usuario tiene un rol específico
        """
        return role.upper() in self.get_roles()

    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'

    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    def get_media_url(self, request=None):
        return build_media_url(self.profile_image, request)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Crear perfil automáticamente al crear un usuario"""
    if created:
        UserProfile.objects.create(user=instance) 

