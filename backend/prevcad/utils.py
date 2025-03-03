from django.conf import settings
import os

def build_media_url(file_field, request=None):
    """
    Builds an absolute media URL for a file field.
    """
    if not file_field:
        return None
        
    try:
        # Obtener la ruta del archivo
        if hasattr(file_field, 'url'):
            file_path = file_field.name
        else:
            file_path = str(file_field)

        # Limpiar la ruta del archivo y quitar cualquier /media/ o /training/ inicial
        file_path = file_path.replace('\\', '/')
        file_path = file_path.lstrip('/')
        file_path = file_path.replace('media/', '')
        file_path = file_path.replace('training/', '')
        
        # Construir URL absoluta
        domain = getattr(settings, 'DOMAIN', 'https://caidas.uchile.cl')
        media_url = f"{domain.rstrip('/')}/media/{file_path}"
        
        print(f"Input file_path: {file_field}")  # Debug
        print(f"Processed file_path: {file_path}")  # Debug
        print(f"Generated media URL: {media_url}")  # Debug
        
        return media_url
            
    except Exception as e:
        print(f"Error building media URL: {str(e)}")
        return None



