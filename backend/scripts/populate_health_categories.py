import os
import sys
import django
import json
import shutil
from django.conf import settings

# [JV] If working without venv, run this
if False:
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if path not in sys.path:
        sys.path.append(path)


# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from prevcad.models import CategoryTemplate

def process_media_file(media_url, media_type='training_videos'):
    """Procesa cualquier archivo de media y retorna la ruta relativa"""
    if not media_url:
        return None

    if media_url.startswith('/training/') or media_url.startswith('training/'):
        source_file = os.path.join(settings.BASE_DIR, 'assets', media_url.lstrip('/'))
        filename = os.path.basename(media_url)
        dest_folder = os.path.join(settings.MEDIA_ROOT, media_type)
        dest_file = os.path.join(dest_folder, filename)

        print(f"Procesando archivo: {filename}")
        print(f"Ruta origen: {source_file}")
        print(f"Ruta destino: {dest_file}")

        os.makedirs(dest_folder, exist_ok=True)

        try:
            if os.path.exists(source_file):
                shutil.copy2(source_file, dest_file)
                relative_path = f'{media_type}/{filename}'
                print(f"✅ Archivo copiado exitosamente: {relative_path}")
                return relative_path
            else:
                print(f"❌ Archivo no encontrado en: {source_file}")
                return None
        except Exception as e:
            print(f"❌ Error copiando archivo {filename}: {e}")
            return None

    return media_url

def process_training_nodes(training_form):
    """Procesa los nodos de entrenamiento"""
    if not training_form or 'training_nodes' not in training_form:
        return training_form

    nodes = training_form['training_nodes']
    nodes.sort(key=lambda x: x.get('order', float('inf')))
    
    for i in range(len(nodes)):
        nodes[i]['next_node_id'] = nodes[i + 1]['id'] if i < len(nodes) - 1 else None

        # Procesar media_url
        if 'media_url' in nodes[i] and nodes[i]['media_url']:
            # Determinar el tipo de media basado en el tipo de nodo
            media_type = 'training_videos' if nodes[i]['type'] == 'VIDEO_NODE' else 'training_images'
            nodes[i]['media_url'] = process_media_file(nodes[i]['media_url'], media_type)

        # Procesar media array
        if 'media' in nodes[i] and nodes[i]['media']:
            for media_item in nodes[i]['media']:
                if 'file' in media_item:
                    original_url = media_item['file'].get('uri') or media_item['file'].get('url')
                    if original_url:
                        media_type = 'training_videos' if nodes[i]['type'] == 'VIDEO_NODE' else 'training_images'
                        relative_path = process_media_file(original_url, media_type)
                        if relative_path:
                            media_item['file']['uri'] = relative_path
                            media_item['file']['url'] = relative_path

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
        # with open(file_path, 'r') as json_file:
        # [JV] required on some systems
        with open(file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

        for template_info in data:
            # Procesar los nodos de entrenamiento
            training_form = process_training_nodes(template_info.get('training_form', {}))
            
            # Procesar el icono
            icon_path = process_icons(template_info.get('icon'))
            
            # Preparar los defaults básicos
            defaults = {
                'description': template_info['description'],
                'is_active': True,
                'icon': icon_path,
                'training_form': training_form,
                'evaluation_form': template_info.get('evaluation_form', None),
                'evaluation_tags': template_info.get('evaluation_tags', [])
            }

            default_recommendations = template_info.get('default_recommendations', {})
            defaults['default_recommendations'] = default_recommendations

            # Manejar el tipo de evaluación y sus formularios
            evaluation_type = template_info.get('evaluation_type', 'SELF')
            defaults['evaluation_type'] = evaluation_type

            
            template, created = CategoryTemplate.objects.update_or_create(
                name=template_info['name'],
                defaults=defaults,
              

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
