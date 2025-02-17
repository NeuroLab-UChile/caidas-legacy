import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from prevcad.models import UserProfile
from django.db.models import Q

def create_missing_profiles():
    # Obtener usuarios sin perfil
    users_without_profile = User.objects.filter(
        Q(profile__isnull=True)
    )
    
    print(f"Encontrados {users_without_profile.count()} usuarios sin perfil")
    
    # Crear perfiles faltantes
    profiles_created = 0
    for user in users_without_profile:
        try:
            UserProfile.objects.create(user=user)
            profiles_created += 1
            print(f"Perfil creado para: {user.username}")
        except Exception as e:
            print(f"Error creando perfil para {user.username}: {str(e)}")
    
    print(f"\nResumen:")
    print(f"Total de usuarios sin perfil: {users_without_profile.count()}")
    print(f"Perfiles creados exitosamente: {profiles_created}")

if __name__ == '__main__':
    print("Iniciando creación de perfiles faltantes...")
    create_missing_profiles()
    print("Proceso completado.")