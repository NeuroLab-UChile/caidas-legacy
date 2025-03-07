from django.core.management.base import BaseCommand
from django.conf import settings
from prevcad.models import UserProfile
import os

class Command(BaseCommand):
    help = 'Diagnostica y corrige problemas con imágenes de perfil'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando diagnóstico de imágenes de perfil...")
        
        # 1. Verificar directorio base
        media_root = settings.MEDIA_ROOT
        profile_images_dir = os.path.join(media_root, 'profile_images')
        
        if not os.path.exists(profile_images_dir):
            os.makedirs(profile_images_dir)
            self.stdout.write(self.style.SUCCESS(
                f'Creado directorio base: {profile_images_dir}'
            ))

        # 2. Revisar cada perfil
        for profile in UserProfile.objects.all():
            self.stdout.write(f"\nRevisando perfil de: {profile.user.username}")
            
            # Mostrar valor actual en la base de datos
            self.stdout.write(f"  Valor en BD: {profile.profile_image}")
            
            if profile.profile_image:
                # Ruta completa del archivo
                image_path = os.path.join(media_root, str(profile.profile_image))
                self.stdout.write(f"  Ruta completa: {image_path}")
                
                # Verificar si el archivo existe
                if not os.path.exists(image_path):
                    self.stdout.write(self.style.WARNING(
                        f"  ⚠️ Imagen no encontrada, limpiando referencia..."
                    ))
                    profile.profile_image = None
                    profile.save(update_fields=['profile_image'])
                else:
                    self.stdout.write(self.style.SUCCESS(
                        f"  ✅ Imagen existe en: {image_path}"
                    ))
            else:
                self.stdout.write("  📝 No tiene imagen asignada")

            # Verificar directorio del usuario
            user_dir = os.path.join(profile_images_dir, str(profile.user.id))
            if not os.path.exists(user_dir):
                os.makedirs(user_dir)
                self.stdout.write(f"  📁 Creado directorio: {user_dir}")
            
            # Listar contenido del directorio
            if os.path.exists(user_dir):
                files = os.listdir(user_dir)
                if files:
                    self.stdout.write("  📂 Archivos en directorio:")
                    for f in files:
                        self.stdout.write(f"    - {f}")
                else:
                    self.stdout.write("  �� Directorio vacío") 