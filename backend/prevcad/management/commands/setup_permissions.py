from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from prevcad.models import UserTypes

class Command(BaseCommand):
    help = 'Configura los permisos de administrador para usuarios existentes'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Encontrar usuarios admin
        admin_users = User.objects.filter(groups__name=UserTypes.ADMIN.value)
        
        for user in admin_users:
            if UserTypes.setup_admin_permissions(user):
                self.stdout.write(
                    self.style.SUCCESS(f'Permisos configurados para {user.username}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'No se pudo configurar permisos para {user.username}')
                ) 