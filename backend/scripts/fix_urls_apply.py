import os
import django
import json
from datetime import datetime

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from prevcad.models import CategoryTemplate, HealthCategory, ActivityNode, ImageNode, VideoNode

def save_backup(data, model_name):
    """Guarda un backup de los datos actuales"""
    backup_dir = os.path.join('scripts', 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{backup_dir}/{model_name}_backup_{timestamp}.json'
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Backup guardado en: {filename}")

def fix_media_path(path, media_type):
    if not path:
        return None
    filename = os.path.basename(path.replace('\\', '/').lstrip('/'))
    
    if media_type == 'video':
        return f'training_videos/{filename}'
    elif media_type == 'image':
        return f'training/{filename}'
    elif media_type == 'icon':
        return f'category_icons/{filename}'
    return path

def apply_fixes():
    print("=== Iniciando corrección de URLs ===")
    
    # 1. Backup y corrección de CategoryTemplates
    templates = CategoryTemplate.objects.all()
    templates_backup = []
    
    for template in templates:
        # Guardar backup
        templates_backup.append({
            'id': template.id,
            'name': template.name,
            'icon': str(template.icon) if template.icon else None,
            'training_form': template.training_form
        })
        
        modified = False
        
        # Corregir icono
        if template.icon:
            new_icon = fix_media_path(str(template.icon), 'icon')
            if str(template.icon) != new_icon:
                template.icon = new_icon
                modified = True
        
        # Corregir training_form
        if template.training_form and 'training_nodes' in template.training_form:
            nodes = template.training_form['training_nodes']
            for node in nodes:
                if 'media_url' in node and node['media_url']:
                    media_type = 'video' if node['type'] == 'VIDEO_NODE' else 'image'
                    new_url = fix_media_path(node['media_url'], media_type)
                    if node['media_url'] != new_url:
                        node['media_url'] = new_url
                        modified = True
            
            template.training_form['training_nodes'] = nodes
        
        if modified:
            template.save()
            print(f"✅ Template actualizado: {template.name}")
    
    save_backup(templates_backup, 'templates')
    
    print("\n=== Proceso completado ===")

if __name__ == '__main__':
    apply_fixes() 