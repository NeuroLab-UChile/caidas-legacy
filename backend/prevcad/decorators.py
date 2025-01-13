from functools import wraps
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.utils import timezone
import logging
from .models.action_log import ActionLog

logger = logging.getLogger(__name__)

def log_action_to_db(user, action_type, description, request=None, extra_data=None):
    """Función auxiliar para registrar acciones en la base de datos"""
    try:
        ActionLog.objects.create(
            timestamp=timezone.now(),
            user=user if user and user.is_authenticated else None,
            action_type=action_type,
            description=description,
            ip_address=request.META.get('REMOTE_ADDR') if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT') if request else None,
            extra_data=extra_data or {}
        )
    except Exception as e:
        logger.error(f"Error registrando acción: {e}")

def doctor_required(view_func):
    """Decorador que verifica si el usuario es doctor y registra las acciones"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Registrar intento de acceso
        log_action_to_db(
            user=request.user,
            action_type='ACCESS_ATTEMPT',
            description=f"Intento de acceso a vista protegida: {request.path}",
            request=request,
            extra_data={'method': request.method, 'path': request.path}
        )

        if not request.user.is_authenticated:
            log_action_to_db(
                user=None,
                action_type='ACCESS_DENIED',
                description="Acceso denegado - Usuario no autenticado",
                request=request
            )
            return JsonResponse({
                'status': 'error',
                'code': 'authentication_required',
                'message': _('Debes iniciar sesión para acceder')
            }, status=401)

        try:
            user_profile = request.user.profile
            user_roles = user_profile.get_roles()
            
            logger.debug(f"User roles: {user_roles}")

            if 'DOCTOR' not in user_roles:
                log_action_to_db(
                    user=request.user,
                    action_type='ACCESS_DENIED',
                    description="Acceso denegado - Rol requerido: DOCTOR",
                    request=request,
                    extra_data={'user_roles': user_roles, 'required_role': 'DOCTOR'}
                )
                return JsonResponse({
                    'status': 'error',
                    'code': 'doctor_required',
                    'message': _('Acceso denegado - Se requiere ser doctor'),
                    'details': {
                        'reason': _('Esta acción requiere ser Doctor'),
                        'current_roles': user_roles,
                        'required_role': 'DOCTOR'
                    }
                }, status=403)

            # Registrar acceso exitoso
            log_action_to_db(
                user=request.user,
                action_type='ACCESS_GRANTED',
                description=f"Acceso exitoso a vista protegida: {request.path}",
                request=request,
                extra_data={'user_roles': user_roles}
            )

            return view_func(request, *args, **kwargs)

        except AttributeError as e:
            logger.error(f"Error accessing user profile: {e}")
            log_action_to_db(
                user=request.user,
                action_type='ERROR',
                description="Error al verificar perfil de usuario",
                request=request,
                extra_data={'error_type': 'profile_error', 'error_message': str(e)}
            )
            return JsonResponse({
                'status': 'error',
                'code': 'profile_error',
                'message': _('Error al verificar el perfil de usuario')
            }, status=500)

    return _wrapped_view

def log_action(action_type, description=None):
    """
    Decorador general para registrar acciones en las vistas.
    Soporta tanto vistas basadas en función como en clase.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            # Determinar si es una vista basada en clase o función
            if len(args) > 0 and hasattr(args[0], 'request'):
                # Vista basada en clase
                self = args[0]
                request = self.request
            else:
                # Vista basada en función
                request = args[0]

            # Ejecutar la vista
            response = view_func(*args, **kwargs)
            
            # Solo registrar si la respuesta fue exitosa
            if hasattr(response, 'status_code') and 200 <= response.status_code < 300:
                try:
                    desc = description(request, *args, **kwargs) if callable(description) else description
                    log_action_to_db(
                        user=request.user,
                        action_type=action_type,
                        description=desc or f"Acción {action_type} en {request.path}",
                        request=request,
                        extra_data={
                            'method': request.method,
                            'path': request.path,
                            'view_type': 'class' if len(args) > 0 and hasattr(args[0], 'request') else 'function',
                            'status_code': response.status_code
                        }
                    )
                except Exception as e:
                    logger.error(f"Error en log_action: {e}")
            
            return response
        return wrapper
    return decorator

# Ejemplo de uso:
"""
@doctor_required
@log_action('UPDATE', 'Actualización de perfil médico')
def update_medical_profile(request):
    # ... código de la vista ...

@log_action('VIEW', 'Visualización de historial médico')
def view_medical_history(request):
    # ... código de la vista ...
"""
