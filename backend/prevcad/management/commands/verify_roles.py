from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from prevcad.models import UserTypes

class Command(BaseCommand):
    help = 'Verifica y corrige roles de usuarios'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Asegurar que existan los grupos básicos
        for role in UserTypes:
            Group.objects.get_or_create(name=role.value)
        
        # Verificar cada usuario
        for user in User.objects.all():
            self.stdout.write(f"\nVerificando usuario: {user.username}")
            
            # Mostrar grupos actuales
            current_groups = user.groups.all()
            self.stdout.write(f"Grupos actuales: {[g.name for g in current_groups]}")
            
            # Si no tiene grupos, asignar PATIENT
            if not current_groups:
                patient_group = Group.objects.get(name=UserTypes.PATIENT.value)
                user.groups.add(patient_group)
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f"Asignado rol PATIENT a {user.username}")
                )
            
            # Verificar perfil
            if hasattr(user, 'profile'):
                self.stdout.write(f"Perfil existe para {user.username}")
            else:
                self.stdout.write(
                    self.style.WARNING(f"Creando perfil para {user.username}")
                )
                from prevcad.models import UserProfile
                UserProfile.objects.create(user=user) 