import os
import django
import sys

# Añadir el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User as OldUser
from django.db import transaction

User = get_user_model()

def migrate_users():
    print("Iniciando migración de usuarios...")
    
    with transaction.atomic():
        for old_user in OldUser.objects.all():
            try:
                # Verificar si el usuario ya existe
                if not User.objects.filter(username=old_user.username).exists():
                    new_user = User.objects.create(
                        username=old_user.username,
                        email=old_user.email or f"{old_user.username}@example.com",
                        password=old_user.password,
                        is_superuser=old_user.is_superuser,
                        is_staff=old_user.is_staff,
                        is_active=old_user.is_active,
                        first_name=old_user.first_name,
                        last_name=old_user.last_name,
                        date_joined=old_user.date_joined
                    )
                    
                    # Copiar grupos
                    for group in old_user.groups.all():
                        new_user.groups.add(group)
                    
                    # Copiar permisos
                    for perm in old_user.user_permissions.all():
                        new_user.user_permissions.add(perm)
                    
                    print(f"Migrado usuario: {new_user.username}")
                else:
                    print(f"Usuario {old_user.username} ya existe, saltando...")
            
            except Exception as e:
                print(f"Error migrando usuario {old_user.username}: {str(e)}")

if __name__ == '__main__':
    try:
        migrate_users()
        print("Migración completada exitosamente")
    except Exception as e:
        print(f"Error durante la migración: {str(e)}") 