from django.conf import settings
import os

def build_media_url(file_field, request=None):
    """
    Builds an absolute media URL for a file field.
    
    Args:
        file_field: FileField object or string path
        request: HttpRequest object (optional)
    
    Returns:
        str: Media URL or file path depending on is_backend
    """
    if not file_field:
        return None
        
    try:
        # Si es un FileField
        if hasattr(file_field, 'url'):
            file_path = file_field.name
        # Si es un string
        else:
            file_path = str(file_field)

        # Limpiar la ruta del archivo
        file_path = file_path.replace('\\', '/').lstrip('/')
        
        if is_backend:
            # Para operaciones de archivo locales
            return os.path.join(settings.MEDIA_ROOT, file_path)
        else:
            # Construir URL absoluta
            if request:
                # Usar el request para construir la URL absoluta
                media_url = request.build_absolute_uri(settings.MEDIA_URL + file_path)
            else:
                # Usar el dominio configurado
                domain = getattr(settings, 'DOMAIN', 'https://caidas.uchile.cl')
                media_url = f"{domain.rstrip('/')}/{settings.MEDIA_URL.lstrip('/')}{file_path}"
            
            print(f"Generated media URL: {media_url}")  # Para debugging
            return media_url
            
    except Exception as e:
        print(f"Error building media URL: {str(e)}")
        return None



