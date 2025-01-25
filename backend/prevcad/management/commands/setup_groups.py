from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from prevcad.models import UserProfile, Appointment, HealthCategory, CategoryTemplate
from prevcad.models.user_types import UserTypes

class Command(BaseCommand):
    help = 'Configura los grupos y permisos basados en UserTypes'

    def handle(self, *args, **kwargs):
        # Obtener content types para los modelos
        appointment_ct = ContentType.objects.get_for_model(Appointment)
        health_category_ct = ContentType.objects.get_for_model(HealthCategory)
        category_template_ct = ContentType.objects.get_for_model(CategoryTemplate)
        user_profile_ct = ContentType.objects.get_for_model(UserProfile)

        # Configurar permisos por tipo de usuario
        permissions_by_type = {
            # Administradores tienen acceso total
            UserTypes.ADMIN: {
                'all': ['add', 'change', 'delete', 'view']
            },
            # Doctores pueden gestionar citas y categorías de salud
            UserTypes.DOCTOR: {
                'appointment': ['add', 'change', 'delete', 'view'],
                'healthcategory': ['change', 'view'],
                'categorytemplate': ['view'],
                'userprofile': ['view', 'change']
            },
            # Enfermeros pueden ver y crear citas
            UserTypes.NURSE: {
                'appointment': ['add', 'change', 'view'],
                'healthcategory': ['view'],
                'userprofile': ['view']
            },
            # Pacientes solo pueden ver su información
            UserTypes.PATIENT: {
                'appointment': ['view'],
                'healthcategory': ['view'],
                'userprofile': ['view']
            }
        }

        # Crear grupos y asignar permisos
        for user_type in UserTypes:
            group, created = Group.objects.get_or_create(name=user_type.value)
            status = 'creado' if created else 'actualizado'
            self.stdout.write(f'Grupo {user_type.value} {status}')

            # Limpiar permisos existentes
            group.permissions.clear()

            # Si el tipo tiene permisos definidos, asignarlos
            if user_type in permissions_by_type:
                perms = permissions_by_type[user_type]
                
                # Si tiene acceso total
                if 'all' in perms:
                    all_perms = Permission.objects.filter(
                        content_type__in=[
                            appointment_ct, 
                            health_category_ct,
                            category_template_ct,
                            user_profile_ct
                        ]
                    )
                    group.permissions.add(*all_perms)
                    self.stdout.write(f'  Asignados todos los permisos a {user_type.value}')
                else:
                    # Asignar permisos específicos
                    for model, actions in perms.items():
                        content_type = {
                            'appointment': appointment_ct,
                            'healthcategory': health_category_ct,
                            'categorytemplate': category_template_ct,
                            'userprofile': user_profile_ct
                        }[model]
                        
                        for action in actions:
                            codename = f'{action}_{model}'
                            try:
                                perm = Permission.objects.get(
                                    codename=codename,
                                    content_type=content_type
                                )
                                group.permissions.add(perm)
                                self.stdout.write(f'  Asignado permiso {codename} a {user_type.value}')
                            except Permission.DoesNotExist:
                                self.stdout.write(
                                    self.style.WARNING(f'  Permiso {codename} no encontrado')
                                )

        self.stdout.write(self.style.SUCCESS('Configuración de grupos completada')) 