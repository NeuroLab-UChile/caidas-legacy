from django.core.management.base import BaseCommand
from django.conf import settings
import os
from prevcad.models import UserProfile

class Command(BaseCommand):
    help = 'Verifica y corrige directorios de media'

    def handle(self, *args, **options):
        # Verificar MEDIA_ROOT
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)
            self.stdout.write(
                self.style.SUCCESS(f'Creado directorio MEDIA_ROOT en {settings.MEDIA_ROOT}')
            )

        # Verificar directorio de imágenes de perfil
        profile_images_dir = os.path.join(settings.MEDIA_ROOT, 'profile_images')
        if not os.path.exists(profile_images_dir):
            os.makedirs(profile_images_dir)
            self.stdout.write(
                self.style.SUCCESS(f'Creado directorio profile_images en {profile_images_dir}')
            )

        # Verificar permisos
        os.chmod(settings.MEDIA_ROOT, 0o755)
        os.chmod(profile_images_dir, 0o755)

        # Verificar directorios de usuarios
        for profile in UserProfile.objects.all():
            user_dir = os.path.join(profile_images_dir, str(profile.user.id))
            if not os.path.exists(user_dir):
                os.makedirs(user_dir)
                os.chmod(user_dir, 0o755)
                self.stdout.write(
                    self.style.SUCCESS(f'Creado directorio para usuario {profile.user.id}')
                )

            # Verificar imagen
            if profile.profile_image:
                image_path = os.path.join(settings.MEDIA_ROOT, str(profile.profile_image))
                if not os.path.exists(image_path):
                    self.stdout.write(
                        self.style.WARNING(
                            f'Imagen no encontrada para {profile.user.username}: {image_path}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Imagen verificada para {profile.user.username}'
                        )
                    ) 