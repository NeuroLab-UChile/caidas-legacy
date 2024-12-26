import os
import django
import json
import shutil
from django.conf import settings

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from prevcad.models import CategoryTemplate

def process_training_nodes(training_form):
    """Procesa los nodos de entrenamiento y copia los videos"""
    if not training_form or 'training_nodes' not in training_form:
        return training_form

    for node in training_form['training_nodes']:
        if 'media_url' in node and node['media_url']:
            if node['media_url'].startswith('/training/'):
                # Construir rutas
                source_video = os.path.join(settings.BASE_DIR, 'assets', node['media_url'].lstrip('/'))
                dest_folder = os.path.join(settings.MEDIA_ROOT, 'training_videos')
                video_filename = os.path.basename(node['media_url'])
                dest_video = os.path.join(dest_folder, video_filename)

                # print(f"Procesando video: {source_video} -> {dest_video}")  # Debug

                # Crear directorio si no existe
                os.makedirs(dest_folder, exist_ok=True)

                try:
                    if os.path.exists(source_video):
                        shutil.copy2(source_video, dest_video)
                        # Modificado: removido /media/ del inicio
                        node['media_url'] = f'training_videos/{video_filename}'
                        print(f"Video copiado exitosamente: {video_filename}")
                    else:
                        print(f"Video no encontrado: {source_video}")
                except Exception as e:
                    print(f"Error copiando video {video_filename}: {e}")

    return training_form

def process_icons(icon_path):
    """Procesa los iconos y los copia de assets a media"""
    print(f"Procesando icono: {icon_path}")
    
    if not icon_path:
        print("No hay ruta de icono")
        return None

    if icon_path.startswith('health_categories_icons/'):
        # Construir rutas
        source_icon = os.path.join(settings.BASE_DIR, 'assets', icon_path)
        dest_folder = os.path.join(settings.MEDIA_ROOT, 'category_icons')
        icon_filename = os.path.basename(icon_path)
        dest_icon = os.path.join(dest_folder, icon_filename)

        print(f"Ruta origen: {source_icon}")
        print(f"Ruta destino: {dest_icon}")

        # Crear directorio si no existe
        os.makedirs(dest_folder, exist_ok=True)

        try:
            if os.path.exists(source_icon):
                shutil.copy2(source_icon, dest_icon)
                print(f"Icono copiado exitosamente: {icon_filename}")
                return f'category_icons/{icon_filename}'
            else:
                print(f"Icono no encontrado en: {source_icon}")
                return None
        except Exception as e:
            print(f"Error copiando icono {icon_filename}: {e}")
            return None

    return icon_path

def populate_category_templates_from_file(file_path):
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)

        for template_info in data:
            # Procesar los nodos de entrenamiento
            training_form = process_training_nodes(template_info.get('training_form', {}))
            
            # Procesar el icono
            icon_path = process_icons(template_info.get('icon'))
            
            template, created = CategoryTemplate.objects.update_or_create(
                name=template_info['name'],
                defaults={
                    'description': template_info['description'],
                    'is_active': True,
                    'evaluation_form': template_info['evaluation_form'],
                    'training_form': training_form,
                    'icon': icon_path
                }
            )

            if created:
                print(f"Creado template: {template.name}")
            else:
                print(f"Actualizado template: {template.name}")

    except FileNotFoundError:
        print(f"Error: El archivo '{file_path}' no se encontró.")
    except json.JSONDecodeError as e:
        print(f"Error al leer el archivo JSON: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(current_dir, 'generated_categories.json')
    
    # Asegurarse de que existen los directorios de medios
    os.makedirs(os.path.join(settings.MEDIA_ROOT, 'training_videos'), exist_ok=True)
    os.makedirs(os.path.join(settings.MEDIA_ROOT, 'category_icons'), exist_ok=True)
    
    populate_category_templates_from_file(json_file_path)
