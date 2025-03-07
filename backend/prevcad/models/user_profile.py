from django.conf import settings
from django.db import models
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import transaction
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from .user_types import UserTypes, AccessLevel, ResourceType
from prevcad.utils import build_media_url
from typing import List, Dict, Optional
import os


class UserProfile(models.Model):
    """Perfil extendido de usuario con roles y permisos."""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name="Teléfono"
    )
    birth_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name="Fecha de nacimiento"
    )
    specialty = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Especialidad del profesional (si aplica)"
    )
    
    def get_profile_image_path(instance, filename):
        """Define la ruta de guardado para la imagen de perfil"""
        ext = os.path.splitext(filename)[1].lower()
        new_filename = f"{uuid.uuid4()}{ext}"
        return os.path.join('profile_images', str(instance.user.id), new_filename)
    
    profile_image = models.ImageField(
        upload_to=get_profile_image_path,  # Usar la función personalizada
        null=True,
        blank=True,
        verbose_name="Foto de perfil"
    )

    @property
    def role(self) -> Optional[str]:
        """Obtiene el rol principal del usuario."""
        group = self.user.groups.first()
        return group.name if group else None

    @property
    def roles(self) -> List[Dict[str, str]]:
        """Obtiene todos los roles del usuario con sus etiquetas."""
        return [
            {
                'value': group.name,
                'label': UserTypes(group.name).label
                if group.name in UserTypes.values else group.name
            }
            for group in self.user.groups.all()
        ]

    def has_permission(self, resource_type: str, action: str) -> bool:
        """
        Verifica si el usuario tiene un permiso específico.
        Args:
            resource_type: Tipo de recurso (usar ResourceType)
            action: Acción requerida ('view', 'add', 'change', 'delete')
        """
        if not self.role:
            return False

        role_config = UserTypes.get_role_config().get(self.role, {})
        
        # Superusuarios tienen todos los permisos
        if role_config.get('level') == AccessLevel.SUPERUSER:
            return True
            
        permissions = role_config.get('permissions', {})
        return action in permissions.get(resource_type, [])

    def has_capability(self, capability: str) -> bool:
        """Verifica si el usuario tiene una capacidad específica."""
        return capability in UserTypes.get_role_capabilities(self.role)

    def get_ui_config(self) -> Dict[str, str]:
        """Obtiene la configuración UI del rol del usuario."""
        return UserTypes.get_role_ui(self.role)

    def is_professional(self) -> bool:
        """Verifica si el usuario es un profesional de la salud."""
        role_config = UserTypes.get_role_config().get(self.role, {})
        return role_config.get('level') == AccessLevel.PROFESSIONAL

    def is_staff_member(self) -> bool:
        """Verifica si el usuario es personal administrativo."""
        role_config = UserTypes.get_role_config().get(self.role, {})
        return role_config.get('level') in [AccessLevel.STAFF, AccessLevel.SUPERUSER]

    def save(self, *args, **kwargs):
        if self.pk and 'profile_image' in kwargs.get('update_fields', []):
            try:
                # Obtener instancia anterior
                old_instance = UserProfile.objects.get(pk=self.pk)
                
                if old_instance.profile_image:
                    # Construir path completo de la imagen anterior
                    old_image_path = os.path.join(settings.MEDIA_ROOT, str(old_instance.profile_image))
                    
                    # Eliminar imagen anterior si existe
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                        
            except Exception as e:
                print(f"Error al eliminar imagen anterior: {str(e)}")

        # Si hay una nueva imagen, asegurar el directorio correcto
        if self.profile_image and hasattr(self.profile_image, 'name'):
            # Crear estructura de directorio
            upload_path = os.path.join('profile_images', str(self.user.id))
            full_media_path = os.path.join(settings.MEDIA_ROOT, upload_path)
            os.makedirs(full_media_path, exist_ok=True)

        super().save(*args, **kwargs)
        
        if not self.user.groups.exists():
            # Asignar rol por defecto
            UserTypes.assign_role(self.user, UserTypes.PATIENT.value)
        elif self.user.groups.filter(name=UserTypes.ADMIN.value).exists():
            # Configurar permisos de admin
            UserTypes.setup_admin_permissions(self.user)

    def set_role(self, role: str):
        """Asigna un nuevo rol al usuario"""
        UserTypes.assign_role(self.user, role)

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

    def delete(self, *args, **kwargs):
        # Eliminar imagen al eliminar el perfil
        if self.profile_image:
            try:
                image_path = os.path.join(settings.MEDIA_ROOT, str(self.profile_image))
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                print(f"Error al eliminar imagen de perfil: {str(e)}")
                
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"

    def __str__(self):
        return f"Perfil de {self.user.get_full_name() or self.user.username}"
    
    def get_media_url(self, request=None):
        return build_media_url(self.profile_image, request)

    def clean(self):
        """
        Validación adicional antes de guardar
        """
        super().clean()
        
        if self.user.groups.filter(name='PATIENT').exists():
            if self.pk:
                original = UserProfile.objects.get(pk=self.pk)
                if (self.profile_image and original.profile_image and 
                    self.profile_image != original.profile_image):
                    raise ValidationError({
                        'profile_image': 'Los pacientes solo pueden cambiar su foto desde la aplicación'
                    })

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Crear perfil automáticamente al crear un usuario"""
    if created:
        UserProfile.objects.create(user=instance) 

