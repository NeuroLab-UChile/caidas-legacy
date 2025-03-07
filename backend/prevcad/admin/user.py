from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from ..models import UserProfile, Appointment, UserTypes
from django.utils import timezone
from threading import current_thread
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Group
from django.conf import settings
import os
import uuid

class AppointmentInline(admin.TabularInline):
    model = Appointment
    extra = 0
    can_delete = True
    verbose_name = "Cita"
    verbose_name_plural = "Citas"
    
    fields = ('date', 'title', 'description', 'user')
    readonly_fields = ('created_at',)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = "Perfil"
    verbose_name_plural = "Perfil de Usuario"
    
    fields = ('preview_image', 'profile_image', 'phone', 'birth_date', 'specialty')
    readonly_fields = ('preview_image',)

    def preview_image(self, obj):
        if obj and obj.profile_image:
            return format_html(
                '<div class="flex flex-col items-center space-y-4">'
                '<div class="w-48 h-48 rounded-full overflow-hidden shadow-lg hover:shadow-xl '
                'transition-all duration-300 transform hover:scale-105">'
                '<img src="{}" class="w-full h-full object-cover"/>'
                '</div>'
                '<span class="text-sm text-gray-600">Foto actual</span>'
                '</div>',
                obj.profile_image.url
            )
        return format_html(
            '<div class="flex flex-col items-center space-y-4">'
            '<div class="w-48 h-48 rounded-full bg-gradient-to-br from-gray-100 to-gray-200 '
            'flex items-center justify-center shadow-md">'
            '<span class="text-4xl text-gray-400">👤</span>'
            '</div>'
            '<span class="text-sm text-gray-600">Sin foto</span>'
            '</div>'
        )
    preview_image.short_description = "Vista previa"

    def save_model(self, request, obj, form, change):
        """
        Maneja el guardado de la imagen de perfil de manera consistente con el frontend
        """
        try:
            if 'profile_image' in form.changed_data and form.cleaned_data['profile_image']:
                image = form.cleaned_data['profile_image']
                
                # Crear el directorio si no existe
                upload_path = f'profile_images/{obj.user.id}'
                full_media_path = os.path.join(settings.MEDIA_ROOT, upload_path)
                os.makedirs(full_media_path, exist_ok=True)

                # Guardar la imagen anterior para posible eliminación
                old_image = obj.profile_image
                
                # Generar nombre único para la imagen
                filename = f"{uuid.uuid4()}{os.path.splitext(image.name)[1].lower()}"
                full_path = os.path.join(upload_path, filename)
                absolute_path = os.path.join(settings.MEDIA_ROOT, full_path)

                # Guardar físicamente la nueva imagen
                with open(absolute_path, 'wb+') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)

                # Actualizar el campo profile_image
                obj.profile_image = full_path

                # Eliminar la imagen anterior si existe
                if old_image:
                    try:
                        old_image_path = os.path.join(settings.MEDIA_ROOT, str(old_image))
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)
                    except Exception as e:
                        print(f"Error al eliminar imagen anterior: {str(e)}")

        except Exception as e:
            print(f"Error guardando imagen de perfil: {str(e)}")
            raise

        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        if obj and obj.groups.filter(name=UserTypes.PATIENT.value).exists():
            readonly_fields.append('profile_image')
        return readonly_fields

# Primero desregistramos el admin por defecto
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    def __init__(self, model, admin_site):
        self.request = None
        super().__init__(model, admin_site)

    def changelist_view(self, request, extra_context=None):
        """Guarda la request para uso en otros métodos"""
        setattr(current_thread(), '_current_request', request)
        return super().changelist_view(request, extra_context)

    def get_list_display(self, request):
        """Guarda la request cuando se obtiene la lista de campos a mostrar"""
        setattr(current_thread(), '_current_request', request)
        return super().get_list_display(request)

    list_display = (
        'get_avatar',
        'username', 
        'get_roles_display',
        'get_full_name',
        'email', 
        'is_active', 
        'get_appointment_count',
        'get_groups',
        'get_permissions_display',
    )
    list_display_links = ('get_avatar', 'username')
    inlines = [UserProfileInline, AppointmentInline]
    
    def has_add_permission(self, request):
        """Permitir que cualquier usuario staff pueda crear usuarios"""
        return request.user.is_staff

    def get_fieldsets(self, request, obj=None):
        if obj is None:  # Cuando se está creando un nuevo usuario
            return (
                (None, {
                    'fields': ('username', 'password1', 'password2')
                }),
                ('Información Personal', {
                    'fields': ('first_name', 'last_name', 'email')
                }),
                ('Permisos Básicos', {
                    'fields': ('is_active', 'groups'),
                }),
            )
        
        # Para edición de usuarios existentes
        fieldsets = [
            (None, {'fields': ('username', 'password')}),
            ('Información Personal', {
                'fields': ('first_name', 'last_name', 'email'),
            }),
        ]
        
        # Mostrar permisos completos solo a admins
        if hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN':
            fieldsets.append(
                ('Permisos', {
                    'fields': (
                        'is_active',
                        'is_staff',
                        'is_superuser',
                        'groups',
                        'user_permissions',
                    ),
                })
            )
        
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        """
        Define campos de solo lectura basados en el rol del usuario
        """
        readonly_fields = super().get_readonly_fields(request, obj)
        
        if obj and obj.groups.filter(name=UserTypes.PATIENT.value).exists():
            # Si es paciente, agregar profile_image a campos de solo lectura
            if hasattr(obj, 'profile'):
                readonly_fields = list(readonly_fields) + ['profile_image']
        
        return readonly_fields

    def save_model(self, request, obj, form, change):
        """Maneja el guardado del usuario y su perfil"""
        super().save_model(request, obj, form, change)
        
        # Asegurar que existe el perfil
        if not hasattr(obj, 'profile'):
            UserProfile.objects.create(user=obj)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email'),
        }),
        ('Permisos Básicos', {
            'fields': ('is_active', 'groups'),
        }),
    )

    def has_change_permission(self, request, obj=None):
        # Verificar si puede editar usuarios
        if obj is None:
            return True  # Puede ver la lista
            
        # Si intenta editar un superusuario
        if obj.is_superuser and not request.user.is_superuser:
            return False
            
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        # Solo los admin pueden eliminar usuarios
        return hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN'

    def get_avatar(self, obj):
        if hasattr(obj, 'profile') and obj.profile.profile_image:
            return format_html(
                '<div class="flex items-center justify-center">'
                '<img src="{}" alt="{}" '
                'class="h-16 w-16 rounded-full object-cover border-2 border-white '
                'shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"/>'
                '</div>',
                obj.profile.profile_image.url,
                obj.username
            )
        return format_html(
            '<div class="flex items-center justify-center">'
            '<div class="h-16 w-16 rounded-full bg-gradient-to-br from-gray-400 to-gray-600 '
            'flex items-center justify-center shadow-lg hover:shadow-xl '
            'transition-all duration-300 hover:scale-105 border-2 border-white">'
            '<span class="text-2xl font-bold text-white">{}</span>'
            '</div>'
            '</div>',
            obj.username[0].upper()
        )
    get_avatar.short_description = 'Foto'

  
    def get_full_name(self, obj):
        """Muestra el nombre completo del usuario de manera segura"""
        full_name = obj.get_full_name()
        return full_name if full_name.strip() else obj.username
    get_full_name.short_description = "Nombre completo"

    def get_appointment_count(self, obj):
        """Muestra el contador de citas de manera segura"""
        try:
            count = obj.appointments.count()
            return format_html(
                '<span class="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm">'
                '{} total</span>',
                count
            )
        except Exception:
            return format_html(
                '<span class="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-sm">'
                '0 total</span>'
            )
    get_appointment_count.short_description = "Citas"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Limitar opciones de grupos según permisos
        if not request.user.is_superuser:
            form.base_fields['groups'].queryset = Group.objects.filter(
                name__in=UserTypes.get_assignable_roles(request.user)
            )
            
            # Deshabilitar campos administrativos
            if 'is_staff' in form.base_fields:
                form.base_fields['is_staff'].disabled = True
            if 'is_superuser' in form.base_fields:
                form.base_fields['is_superuser'].disabled = True
                
        return form

    def get_queryset(self, request):
        """Optimizar consultas para incluir perfiles y grupos"""
        return super().get_queryset(request).prefetch_related(
            'groups',
            'profile'
        )

    def get_groups(self, obj):
        """Muestra todos los grupos del usuario"""
        groups = obj.groups.all()
        if not groups:
            return format_html(
                '<span class="text-red-600">Sin grupos</span>'
            )
        return format_html(
            ', '.join([g.name for g in groups])
        )
    get_groups.short_description = "Grupos"

    def get_roles_display(self, obj):
        """
        Muestra todos los roles del usuario con badges
        """
        try:
            groups = obj.groups.all()
            if not groups:
                return format_html(
                    '<span class="badge badge-warning">Sin rol</span>'
                )

            badges = []
            for group in groups:
                try:
                    role = UserTypes(group.name)
                    badges.append(
                        format_html(
                            '<span class="badge badge-{}">{} {}</span>',
                            role.value.lower(),
                            self._get_role_icon(role.value),
                            role.label
                        )
                    )
                except ValueError:
                    badges.append(
                        format_html(
                            '<span class="badge badge-default">{}</span>',
                            group.name
                        )
                    )

            return format_html(
                '<div class="role-badges">{}</div>',
                format_html(' '.join(badges))
            )
        except Exception as e:
            print(f"Error mostrando roles para {obj.username}: {str(e)}")
            return format_html(
                '<span class="badge badge-error">Error</span>'
            )

    get_roles_display.short_description = "Roles"

    def _get_role_icon(self, role):
        """Retorna el icono correspondiente al rol"""
        icons = {
            'ADMIN': '👑',
            'DOCTOR': '👨‍⚕️',
            'PATIENT': '🏥',
            'CARDIOLOGIST': '❤️',
            'DENTIST': '🦷',
            'NURSE': '💉',
            'PSYCHOLOGIST': '🧠',
            'PHYSIOTHERAPIST': '💪',
            'NUTRITIONIST': '🥗',
            'COORDINATOR': '📋',
            'MANAGER': '📊',
            'RECEPTIONIST': '📝',
        }
        return icons.get(role, '👤')

    def get_permissions_display(self, obj):
        """Muestra los permisos del usuario"""
        permissions = []
        
        if obj.is_superuser:
            permissions.append(
                '<span class="badge badge-superuser">Superusuario</span>'
            )
        if obj.is_staff:
            permissions.append(
                '<span class="badge badge-staff">Staff</span>'
            )
            
        if not permissions:
            return format_html(
                '<span class="badge badge-basic">Usuario básico</span>'
            )
            
        return format_html(
            '<div class="permission-badges">{}</div>',
            format_html(' '.join(permissions))
        )
    
    get_permissions_display.short_description = "Permisos"

    class Media:
        css = {
            'all': (
                'https://cdn.tailwindcss.com',
                'admin/css/forms.css',
                'admin/css/widgets.css',
                'admin/css/custom_admin.css',
            )
        }
        js = (
            'admin/js/core.js',
            'admin/js/vendor/jquery/jquery.js',
            'admin/js/jquery.init.js',
        )

    def get_readonly_fields(self, request, obj=None):
        """
        Hace el campo profile_image de solo lectura para pacientes
        """
        readonly_fields = super().get_readonly_fields(request, obj)
        
        if obj and obj.groups.filter(name=UserTypes.PATIENT.value).exists():
            readonly_fields = list(readonly_fields) + ['profile_image']
            
        return readonly_fields
    
    def has_change_permission(self, request, obj=None):
        """
        Verifica permisos de edición para el perfil
        """
        if obj and obj.groups.filter(name=UserTypes.PATIENT.value).exists():
            # Si es paciente, no permitir edición de la foto
            return False
        return super().has_change_permission(request, obj)
