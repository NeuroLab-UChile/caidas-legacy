from django.conf import settings
import os

def build_media_url(file_path, request=None, is_backend=True):
    """
    Builds a media URL or file path for a file field.
    
    Args:
        file_path: File path
        request: HttpRequest object (optional)
        is_backend: Boolean indicating if the request is for backend file operations
    
    Returns:
        str: Media URL or file path depending on is_backend
    """
    if not file_path:
        return None
        
    try:
        if is_backend:
            # Para operaciones de archivo locales (como get_icon_base64)
            print(f"file_path: {file_path}")
            if type(file_path) == str:
                return os.path.join(settings.MEDIA_ROOT, file_path)
            else:
                return os.path.join(settings.MEDIA_ROOT, file_path.name)
            
        elif request:
            # Para URLs absolutas en respuestas API
            return request.build_absolute_uri(f"{settings.MEDIA_URL}{file_path}")
        else:
            # Para URLs relativas
            if type(file_path) == str:
                return f"{settings.DOMAIN}/{settings.MEDIA_URL}{file_path}"
            else:
                return f"{settings.DOMAIN}/{settings.MEDIA_URL}{file_path}"
            
    except Exception as e:
        print(f"Error building media URL: {str(e)}")
        return None



