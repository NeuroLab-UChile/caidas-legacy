import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User as OldUser
from prevcad.models import User as NewUser

def migrate_users():
    for old_user in OldUser.objects.all():
        new_user = NewUser.objects.create(
            username=old_user.username,
            email=old_user.email,
            password=old_user.password,  # La contraseña ya está hasheada
            is_superuser=old_user.is_superuser,
            is_staff=old_user.is_staff,
            is_active=old_user.is_active,
            first_name=old_user.first_name,
            last_name=old_user.last_name,
            date_joined=old_user.date_joined
        )
        print(f"Migrado usuario: {new_user.username}")

if __name__ == '__main__':
    migrate_users() 