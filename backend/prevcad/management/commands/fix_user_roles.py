from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from prevcad.models import UserProfile, UserTypes

class Command(BaseCommand):
    help = 'Arregla roles y perfiles de usuarios existentes'

    def handle(self, *args, **options):
        User = get_user_model()
        
        for user in User.objects.all():
            # Asegurar que existe el perfil
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Si no tiene rol, asignar el default
            if not user.groups.exists():
                if UserTypes.assign_role(user, UserTypes.get_default_role()):
                    self.stdout.write(
                        self.style.SUCCESS(f'Rol asignado a {user.username}')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'Error asignando rol a {user.username}')
                    ) 