from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from enum import Enum
from typing import List, Dict, Any, Optional
from django.core.exceptions import PermissionDenied

class AccessLevel(Enum):
    SUPERUSER = "superuser"
    STAFF = "staff"
    PROFESSIONAL = "professional"
    PATIENT = "patient"
    NONE = "none"

class ResourceType(Enum):
    USERS = "users"
    CATEGORIES = "categories"
    RECOMMENDATIONS = "recommendations"
    APPOINTMENTS = "appointments"
    EVALUATIONS = "evaluations"
    TEMPLATES = "templates"
    MEDICAL_RECORDS = "medical_records"

class UserTypes(models.TextChoices):
    """
    Define los tipos de usuarios y sus permisos en el sistema.
    Cada tipo tiene un conjunto específico de capacidades y accesos.
    """
    
    # Roles principales
    ADMIN = 'ADMIN', 'Administrador'
    DOCTOR = 'DOCTOR', 'Doctor'
    PATIENT = 'PATIENT', 'Paciente'
    
    # Profesionales de la salud
    NUTRITIONIST = 'NUTRITIONIST', 'Nutricionista'
    PHYSIOTHERAPIST = 'PHYSIOTHERAPIST', 'Fisioterapeuta'
    PSYCHOLOGIST = 'PSYCHOLOGIST', 'Psicólogo'
    NURSE = 'NURSE', 'Enfermero'
    DENTIST = 'DENTIST', 'Dentista'
    CARDIOLOGIST = 'CARDIOLOGIST', 'Cardiólogo'
    PEDIATRICIAN = 'PEDIATRICIAN', 'Pediatra'
    
    # Personal administrativo
    RECEPTIONIST = 'RECEPTIONIST', 'Recepcionista'
    COORDINATOR = 'COORDINATOR', 'Coordinador'
    MANAGER = 'MANAGER', 'Gerente'

    @classmethod
    def setup_admin_permissions(cls, user):
        """
        Configura los permisos de administrador correctamente
        """
        if not user.groups.filter(name=cls.ADMIN.value).exists():
            return False

        # Hacer al usuario staff y superuser
        user.is_staff = True
        user.is_superuser = True
        user.save()

        # Obtener o crear el grupo admin
        admin_group, _ = Group.objects.get_or_create(name=cls.ADMIN.value)

        # Asignar todos los permisos disponibles al grupo admin
        all_permissions = Permission.objects.all()
        admin_group.permissions.set(all_permissions)

        return True

    @classmethod
    def get_role_config(cls) -> dict:
        """Define la configuración de cada rol"""
        return {
            cls.ADMIN.value: {
                'level': AccessLevel.SUPERUSER,
                'is_staff': True,
                'is_superuser': True,
                'permissions': {
                    ResourceType.USERS: ['view', 'add', 'change', 'delete'],
                    ResourceType.CATEGORIES: ['view', 'add', 'change', 'delete'],
                    ResourceType.RECOMMENDATIONS: ['view', 'add', 'change', 'delete'],
                    ResourceType.APPOINTMENTS: ['view', 'add', 'change', 'delete'],
                    ResourceType.EVALUATIONS: ['view', 'add', 'change', 'delete'],
                    ResourceType.TEMPLATES: ['view', 'add', 'change', 'delete'],
                    ResourceType.MEDICAL_RECORDS: ['view', 'add', 'change', 'delete'],
                },
            },
            cls.DOCTOR.value: {
                'level': AccessLevel.PROFESSIONAL,
                'is_staff': True,
                'is_superuser': False,
            },
            cls.CARDIOLOGIST.value: {
                'level': AccessLevel.PROFESSIONAL,
                'is_staff': True,
                'is_superuser': False,
            },
            cls.DENTIST.value: {
                'level': AccessLevel.PROFESSIONAL,
                'is_staff': True,
                'is_superuser': False,
            },
            cls.PATIENT.value: {
                'level': AccessLevel.PATIENT,
                'is_staff': False,
                'is_superuser': False,
            }
        }

    @classmethod
    def get_role_permissions(cls, role: str) -> Dict[str, List[str]]:
        """Obtiene los permisos específicos de un rol."""
        return cls.get_role_config().get(role, {}).get('permissions', {})

    @classmethod
    def get_role_capabilities(cls, role: str) -> List[str]:
        """Obtiene las capacidades específicas de un rol."""
        return cls.get_role_config().get(role, {}).get('capabilities', [])

    @classmethod
    def get_role_ui(cls, role: str) -> dict:
        """Configuración UI mejorada para roles"""
        configs = {
            cls.ADMIN.value: {
                'badge_class': 'bg-purple-100 text-purple-800',
                'icon': '👑'
            },
            cls.DOCTOR.value: {
                'badge_class': 'bg-blue-100 text-blue-800',
                'icon': '👨‍⚕️'
            },
            cls.PATIENT.value: {
                'badge_class': 'bg-green-100 text-green-800',
                'icon': '🏥'
            },
            cls.NURSE.value: {
                'badge_class': 'bg-indigo-100 text-indigo-800',
                'icon': '👨‍⚕️'
            },
            # ... otros roles ...
        }
        
        return configs.get(role, {
            'badge_class': 'bg-gray-100 text-gray-800',
            'icon': '👤'
        })

    @classmethod
    def has_permission(cls, user, permission_type, action):
        """
        Verifica si un usuario tiene un permiso específico
        Args:
            user: Usuario a verificar
            permission_type: Tipo de permiso (ej: 'recommendations')
            action: Acción requerida ('view', 'add', 'change', 'delete')
        Returns:
            bool: True si tiene permiso, False si no
        """
        if not hasattr(user, 'profile') or not user.profile.role:
            return False

        role_config = cls.get_role_config().get(user.profile.role, {})
        
        # Superusuarios tienen todos los permisos
        if role_config.get('level') == AccessLevel.SUPERUSER:
            return True
            
        permissions = role_config.get('permissions', {})
        return action in permissions.get(permission_type, [])

    @classmethod
    def get_access_level(cls, role):
        """Obtiene el nivel de acceso de un rol"""
        return cls.get_role_config().get(role, {}).get('level', AccessLevel.NONE)

    @classmethod
    def is_professional(cls, role):
        """Verifica si un rol es profesional"""
        return role in [r[0] for r in cls.get_professional_types()]

    @classmethod
    def is_staff(cls, role):
        """Verifica si un rol es de staff"""
        level = cls.get_role_config().get(role, {}).get('level')
        return level in [AccessLevel.STAFF, AccessLevel.SUPERUSER]

    @classmethod
    def assign_role(cls, user, role: str, assigner=None):
        """
        Asigna un rol a un usuario y configura sus permisos
        """
        try:
            # Validar que el rol existe
            valid_role = cls(role)
            role_config = cls.get_role_config().get(valid_role.value, {})

            # Limpiar grupos existentes
            user.groups.clear()
            
            # Obtener o crear el grupo
            group, _ = Group.objects.get_or_create(name=valid_role.value)
            
            # Asignar el grupo
            user.groups.add(group)
            
            # Configurar permisos según el rol
            user.is_staff = role_config.get('is_staff', False)
            user.is_superuser = role_config.get('is_superuser', False)
            
            # Asegurarse de que los pacientes nunca sean staff
            if valid_role == cls.PATIENT:
                user.is_staff = False
                user.is_superuser = False
            
            user.save()
            
            return True
        except Exception as e:
            print(f"Error asignando rol {role} a {user.username}: {str(e)}")
            return False

    @classmethod
    def can_manage_roles(cls, user) -> bool:
        """Verifica si un usuario puede gestionar roles"""
        if not hasattr(user, 'profile') or not user.profile.role:
            return False
            
        return user.is_superuser or user.profile.role == cls.ADMIN.value

    @classmethod
    def is_admin_role(cls, role: str) -> bool:
        """Verifica si un rol es administrativo"""
        return role in [cls.ADMIN.value, cls.MANAGER.value]

    @classmethod
    def get_assignable_roles(cls, assigner) -> List[str]:
        """
        Obtiene los roles que un usuario puede asignar
        """
        if not cls.can_manage_roles(assigner):
            return []
            
        if assigner.is_superuser:
            return list(cls.values)
            
        # Administradores no pueden asignar roles administrativos
        return [role for role in cls.values 
               if not cls.is_admin_role(role)]

    @classmethod
    def fix_patient_permissions(cls):
        """
        Corrige permisos de pacientes existentes
        """
        User = get_user_model()
        patient_users = User.objects.filter(groups__name=cls.PATIENT.value)
        
        for user in patient_users:
            user.is_staff = False
            user.is_superuser = False
            user.save()

    @classmethod
    def get_professional_types(cls):
        """Retorna lista de roles profesionales"""
        professional_roles = [
            cls.DOCTOR,
            cls.NUTRITIONIST,
            cls.PHYSIOTHERAPIST,
            cls.PSYCHOLOGIST,
            cls.NURSE,
            cls.DENTIST,
            cls.CARDIOLOGIST,
            cls.PEDIATRICIAN
        ]
        return [
            (role.value, role.label) 
            for role in professional_roles
        ]

@receiver(post_migrate)
def create_user_groups(sender, **kwargs):
    """
    Crea los grupos de usuarios después de la migración
    """
    # Solo ejecutar para la app 'prevcad'
    if sender.name != 'prevcad':
        return

    for user_type in UserTypes:
        group, created = Group.objects.get_or_create(name=user_type.value)
        if created:
            print(f"Grupo creado: {user_type.value}") 