import os
import django
import json

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from prevcad.models import CategoryTemplate

def populate_category_templates_from_file(file_path):
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)

        for template_info in data:
            # Construct the icon path relative to assets folder
            icon_path = f"{template_info['icon']}" if template_info.get('icon') else None
            
            template, created = CategoryTemplate.objects.update_or_create(
                name=template_info['name'],
                defaults={
                    'description': template_info['description'],
                    'is_active': True,
                    'evaluation_form': template_info['evaluation_form'],
                    'training_form': template_info['training_form'],
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

 
    populate_category_templates_from_file(json_file_path)
