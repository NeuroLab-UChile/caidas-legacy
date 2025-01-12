from functools import wraps
from django.http import JsonResponse
from django.utils.translation import gettext as _
import logging

logger = logging.getLogger(__name__)

def doctor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({
                'status': 'error',
                'code': 'authentication_required',
                'message': _('Debes iniciar sesión para acceder')
            }, status=401)

        try:
            user_profile = request.user.profile
            # Obtener roles como lista
            user_roles = user_profile.get_roles()
            
            logger.debug(f"User roles: {user_roles}")
            logger.debug(f"Is doctor in roles?: {'DOCTOR' in user_roles}")

            # Verificar si DOCTOR está en los roles del usuario
            if 'DOCTOR' not in user_roles:
                return JsonResponse({
                    'status': 'error',
                    'code': 'doctor_required',
                    'message': _('Acceso denegado - Se requiere ser doctor'),
                    'details': {
                        'reason': _('Esta acción requiere ser Doctor'),
                        'current_roles': user_roles,
                        'required_role': 'DOCTOR',
                        'debug_info': {
                            'all_roles': user_roles,
                            'has_doctor_role': 'DOCTOR' in user_roles
                        }
                    }
                }, status=403)

            return view_func(request, *args, **kwargs)

        except AttributeError as e:
            logger.error(f"Error accessing user profile: {e}")
            return JsonResponse({
                'status': 'error',
                'code': 'profile_error',
                'message': _('Error al verificar el perfil de usuario')
            }, status=500)
        except Exception as e:
            logger.error(f"Unexpected error in doctor_required decorator: {e}")
            return JsonResponse({
                'status': 'error',
                'code': 'unknown_error',
                'message': _('Error inesperado al verificar permisos')
            }, status=500)

    return _wrapped_view
