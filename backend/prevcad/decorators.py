from functools import wraps
from django.http import JsonResponse
from django.utils.translation import gettext as _
import logging

logger = logging.getLogger(__name__)

def doctor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        response_params = {
            'json_dumps_params': {'indent': 2, 'ensure_ascii': False},
            'content_type': 'application/json'
        }

        # Debug: Imprimir información del usuario
        logger.debug(f"User: {request.user.username}")
        logger.debug(f"Is authenticated: {request.user.is_authenticated}")
        
        try:
            user_profile = request.user.profile  # Usando related_name 'profile'
            logger.debug(f"User role: {user_profile.role}")
            logger.debug(f"Role type: {type(user_profile.role)}")
            logger.debug(f"Is doctor?: {user_profile.role == 'doctor'}")
            
            # Verificar el rol usando valores de las constantes
            if user_profile.role.lower() != 'doctor':  # Normalizar a minúsculas
                return JsonResponse({
                    'status': 'error',
                    'code': 'doctor_required',
                    'message': _('Acceso denegado - Se requiere ser doctor'),
                    'details': {
                        'reason': _(f'Tu rol actual es {user_profile.get_role_display()}, pero esta acción requiere ser Doctor'),
                        'current_role': user_profile.get_role_display(),
                        'required_role': 'Doctor',
                        'debug_info': {
                            'role_value': user_profile.role,
                            'role_type': str(type(user_profile.role)),
                            'role_display': user_profile.get_role_display()
                        }
                    }
                }, status=403, **response_params)

        except Exception as e:
            logger.error(f"Error checking doctor role: {str(e)}", exc_info=True)
            return JsonResponse({
                'status': 'error',
                'code': 'role_check_error',
                'message': _('Error verificando rol'),
                'details': {
                    'error': str(e),
                    'type': str(type(e))
                }
            }, status=500, **response_params)

        return view_func(request, *args, **kwargs)

    return _wrapped_view
