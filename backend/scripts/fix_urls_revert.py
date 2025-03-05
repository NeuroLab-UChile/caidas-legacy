import os
import django
import json
import glob

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from prevcad.models import CategoryTemplate, HealthCategory, ActivityNode, ImageNode, VideoNode

def get_latest_backup(model_name):
    """Obtiene el backup más reciente"""
    backup_dir = os.path.join('scripts', 'backups')
    pattern = f'{backup_dir}/{model_name}_backup_*.json'
    files = glob.glob(pattern)
    
    if not files:
        raise Exception(f"No se encontró backup para {model_name}")
        
    latest = max(files)
    print(f"Usando backup: {latest}")
    
    with open(latest, 'r') as f:
        return json.load(f)

def revert_changes():
    print("=== Iniciando reversión de URLs ===")
    
    try:
        # Revertir CategoryTemplates
        templates_backup = get_latest_backup('templates')
        
        for backup in templates_backup:
            template = CategoryTemplate.objects.get(id=backup['id'])
            template.icon = backup['icon']
            template.training_form = backup['training_form']
            template.save()
            print(f"✅ Template revertido: {template.name}")
            
        print("\n=== Reversión completada ===")
        
    except Exception as e:
        print(f"❌ Error durante la reversión: {str(e)}")

if __name__ == '__main__':
    revert_changes() 