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
    """Procesa los nodos de entrenamiento usando la misma lógica que los iconos"""
    if not training_form or 'training_nodes' not in training_form:
        return training_form

    nodes = training_form['training_nodes']
    nodes.sort(key=lambda x: x.get('order', float('inf')))
    
    for i in range(len(nodes)):
        nodes[i]['next_node_id'] = nodes[i + 1]['id'] if i < len(nodes) - 1 else None

        # Procesar media_url usando la misma lógica que los iconos
        if 'media_url' in nodes[i] and nodes[i]['media_url']:
            media_url = nodes[i]['media_url']
            print(f"Procesando media_url: {media_url}")

            if media_url.startswith('/training/') or media_url.startswith('training/'):
                source_video = os.path.join(settings.BASE_DIR, 'assets', media_url.lstrip('/'))
                video_filename = os.path.basename(media_url)
                dest_folder = os.path.join(settings.MEDIA_ROOT, 'training_videos')
                dest_video = os.path.join(dest_folder, video_filename)

                print(f"Ruta origen: {source_video}")
                print(f"Ruta destino: {dest_video}")

                os.makedirs(dest_folder, exist_ok=True)

                try:
                    if os.path.exists(source_video):
                        shutil.copy2(source_video, dest_video)
                        # Usar la misma lógica que los iconos
                        nodes[i]['media_url'] = f'training_videos/{video_filename}'
                        print(f"✅ Video copiado exitosamente: {video_filename}")
                    else:
                        print(f"❌ Video no encontrado en: {source_video}")
                except Exception as e:
                    print(f"❌ Error copiando video {video_filename}: {e}")

        # Procesar media array con la misma lógica
        if 'media' in nodes[i] and nodes[i]['media']:
            for media_item in nodes[i]['media']:
                if 'file' in media_item and (media_item['file'].get('uri') or media_item['file'].get('url')):
                    original_url = media_item['file'].get('uri') or media_item['file'].get('url')
                    if original_url and (original_url.startswith('/training/') or original_url.startswith('training/')):
                        source_video = os.path.join(settings.BASE_DIR, 'assets', original_url.lstrip('/'))
                        video_filename = os.path.basename(original_url)
                        dest_folder = os.path.join(settings.MEDIA_ROOT, 'training_videos')
                        dest_video = os.path.join(dest_folder, video_filename)

                        os.makedirs(dest_folder, exist_ok=True)

                        try:
                            if os.path.exists(source_video):
                                shutil.copy2(source_video, dest_video)
                                # Usar la misma lógica que los iconos
                                relative_path = f'training_videos/{video_filename}'
                                media_item['file']['uri'] = relative_path
                                media_item['file']['url'] = relative_path
                                print(f"✅ Video en media copiado exitosamente: {video_filename}")
                            else:
                                print(f"❌ Video en media no encontrado: {source_video}")
                        except Exception as e:
                            print(f"❌ Error copiando video en media {video_filename}: {e}")

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
