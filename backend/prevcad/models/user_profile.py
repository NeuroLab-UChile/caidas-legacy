from django.db import models
from django.contrib.auth.models import User, Group
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
        related_name='profile'
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
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
    def role(self):
        """Obtiene el rol del usuario basado en su grupo"""
        return self.user.groups.first().name if self.user.groups.exists() else None

    @role.setter
    def role(self, role_name):
        """Establece el rol del usuario cambiando su grupo"""
        if role_name not in UserTypes.values:
            raise ValueError(f"Rol inválido: {role_name}")
        
        # Limpiar grupos existentes
        self.user.groups.clear()
        
        # Agregar al nuevo grupo
        group = Group.objects.get(name=role_name)
        self.user.groups.add(group)
        
        # Actualizar is_staff según el tipo de usuario
        self.user.is_staff = UserTypes.is_professional(role_name) or UserTypes.is_staff(role_name)
        self.user.save()

    def is_professional(self):
        """Verifica si el usuario es un profesional de la salud"""
        return UserTypes.is_professional(self.role)

    def is_staff_member(self):
        """Verifica si el usuario es personal administrativo"""
        return UserTypes.is_staff(self.role)

    def save(self, *args, **kwargs):
        creating = not self.pk
        super().save(*args, **kwargs)
        
        if creating and not self.user.groups.exists():
            # Por defecto, asignar como paciente
            self.role = UserTypes.PATIENT

    def get_roles(self):
        """
        Retorna lista de roles del usuario.
        Si el rol está almacenado como string múltiple, lo divide.
        """
        if not self.role:
            return []
            
        # Si el rol contiene múltiples roles separados por algún delimitador
        if ',' in self.role:
            return [role.strip().upper() for role in self.role.split(',')]
        if '_' in self.role:
            return [role.strip().upper() for role in self.role.split('_')]
            
        # Si es un solo rol
        return [self.role.upper()]

    def has_role(self, role):
        """
        Verifica si el usuario tiene un rol específico
        """
        return role.upper() in self.get_roles()

    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'

    def __str__(self):
        role = self.role or 'Sin rol'
        return f"{self.user.username} - {role}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crear perfil automáticamente al crear un usuario"""
    if created:
        UserProfile.objects.create(user=instance) 
