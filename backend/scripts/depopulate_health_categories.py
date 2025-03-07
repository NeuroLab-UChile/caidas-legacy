import os
import django
import shutil
from django.conf import settings
import glob
import subprocess

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from prevcad.models import CategoryTemplate, VideoNode, ImageNode, HealthCategory

def force_delete_directory(path):
    """Fuerza la eliminación de un directorio usando comandos del sistema"""
    try:
        if os.path.exists(path):
            # Primero intenta con shutil
            shutil.rmtree(path, ignore_errors=True)
            
            # Si aún existe, usa comando del sistema
            if os.path.exists(path):
                if os.name == 'nt':  # Windows
                    subprocess.run(['rd', '/s', '/q', path], shell=True)
                else:  # Unix/Linux/MacOS
                    subprocess.run(['rm', '-rf', path])
                    
            print(f"✅ Forzada eliminación de: {path}")
    except Exception as e:
        print(f"Error eliminando {path}: {e}")

def clean_media_aggressive():
    """Limpieza agresiva de todos los directorios de media"""
    media_root = settings.MEDIA_ROOT
    
    # Lista de directorios a eliminar
    directories_to_clean = [
        'training_videos',
        'category_icons',
        'evaluation_images',
        'images',
        'profile_images',
        'recommendations',
        'uploads',
        'videos'
    ]
    
    print("\nIniciando limpieza agresiva...")
    
    # Eliminar cada directorio específico
    for directory in directories_to_clean:
        dir_path = os.path.join(media_root, directory)
        force_delete_directory(dir_path)
        
    # Eliminar cualquier archivo suelto en media_root
    for item in glob.glob(os.path.join(media_root, '*')):
        if os.path.isfile(item):
            os.remove(item)
            print(f"✅ Archivo eliminado: {item}")
        elif os.path.isdir(item):
            force_delete_directory(item)
    
    # Recrear estructura básica
    os.makedirs(media_root, exist_ok=True)
    print("\n✅ Directorio media recreado limpio")

def clean_database():
    """Limpia la base de datos"""
    try:
        VideoNode.objects.all().delete()
        ImageNode.objects.all().delete()
        CategoryTemplate.objects.all().delete()
        HealthCategory.objects.all().delete()
        print("✅ Base de datos limpiada")
    except Exception as e:
        print(f"Error limpiando base de datos: {e}")

def clean_media_directory(media_type):
    """Limpia un directorio específico de media"""
    dir_path = os.path.join(settings.MEDIA_ROOT, media_type)
    if os.path.exists(dir_path):
        try:
            shutil.rmtree(dir_path)
            print(f"✅ Limpiado directorio: {media_type}")
            # Recrear el directorio vacío
            os.makedirs(dir_path, exist_ok=True)
            return True
        except Exception as e:
            print(f"❌ Error limpiando {media_type}: {e}")
            return False
    return True

def depopulate_category_templates():
    """
    Elimina todas las categorías y limpia los archivos de media asociados.
    Sigue la misma estructura que populate_category_templates_from_file.
    """
    try:
        print("\n=== Iniciando despoblación de categorías ===")

        # 1. Eliminar todas las categorías de salud
        health_count = HealthCategory.objects.count()
        HealthCategory.objects.all().delete()
        print(f"✅ Eliminadas {health_count} categorías de salud")

        # 2. Eliminar todos los templates
        template_count = CategoryTemplate.objects.count()
        CategoryTemplate.objects.all().delete()
        print(f"✅ Eliminados {template_count} templates de categoría")

        # 3. Limpiar directorios de media (siguiendo la estructura de populate)
        media_types = [
            'training_videos',    # Para VIDEO_NODE
            'training_images',    # Para IMAGE_NODE y DESCRIPTION_NODE
            'category_icons',     # Para iconos de categoría
            'evaluation_images'   # Para imágenes de evaluación
        ]

        print("\n=== Limpiando directorios de media ===")
        for media_type in media_types:
            clean_media_directory(media_type)

        print("\n✅ Despoblación completada exitosamente")
        return True

    except Exception as e:
        print(f"\n❌ Error durante la despoblación: {e}")
        return False

if __name__ == '__main__':
    print("🧹 Iniciando limpieza de la base de datos...")
    success = depopulate_category_templates()
    
    if success:
        print("\n=== Resumen de la limpieza ===")
        print("✓ Categorías de salud eliminadas")
        print("✓ Templates eliminados")
        print("✓ Directorios de media limpiados")
    else:
        print("\n❌ La limpieza no se completó correctamente") 