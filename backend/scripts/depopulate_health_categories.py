import os
import django
import shutil
from django.conf import settings
import glob
import subprocess

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from prevcad.models import CategoryTemplate, VideoNode, ImageNode

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
        print("✅ Base de datos limpiada")
    except Exception as e:
        print(f"Error limpiando base de datos: {e}")

if __name__ == '__main__':
    print("=== LIMPIEZA AGRESIVA DEL SISTEMA ===")
    confirmation = input("⚠️  Esto eliminará TODOS los archivos. Escribe 'FORCE DELETE' para confirmar: ")
    
    if confirmation == 'FORCE DELETE':
        print("\nEjecutando limpieza agresiva...")
        clean_database()
        clean_media_aggressive()
        
        # Verificación final
        print("\nVerificando archivos residuales...")
        remaining_files = glob.glob(os.path.join(settings.MEDIA_ROOT, '**/*'), recursive=True)
        if remaining_files:
            print("Archivos restantes encontrados:")
            for file in remaining_files:
                print(f"- {file}")
        else:
            print("✅ No se encontraron archivos residuales")
            
        print("\n✅ Proceso de limpieza completado")
    else:
        print("\n❌ Operación cancelada") 