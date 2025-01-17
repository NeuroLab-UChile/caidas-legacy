from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from ..models import UserProfile, Appointment
from django.utils import timezone
from threading import current_thread

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
        'get_full_name',
        'get_role_badge',
        'email', 
        'is_active', 
        'get_appointment_count'
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
        if obj is None:  # Si es creación, no hay campos de solo lectura
            return []
            
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'ADMIN':
            return [
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ]
        return []

    def save_model(self, request, obj, form, change):
        if not change:  # Si es un nuevo usuario
            obj.is_staff = True  # Hacer staff por defecto
            # Asegurarse de que se guarde la contraseña correctamente
            if hasattr(form, 'cleaned_data'):
                password = form.cleaned_data.get('password1')
                if password:
                    obj.set_password(password)
        
        super().save_model(request, obj, form, change)

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
        return request.user.is_staff

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

    def get_role_badge(self, obj):
        """Muestra el rol del usuario y si es el usuario actual"""
        try:
            # Debug para ver los valores
            request = getattr(current_thread(), '_current_request', None)
            print(f"""
            Debug get_role_badge:
            - Request exists: {bool(request)}
            - Request user: {request.user.id if request and hasattr(request, 'user') else None}
            - Object user: {obj.id}
            - Is same user: {request and request.user.id == obj.id}
            """)

            # Verificación más segura del usuario actual
            is_current_user = (
                request and 
                hasattr(request, 'user') and 
                request.user.is_authenticated and 
                request.user.id == obj.id
            )
            
            role = obj.profile.role
            role_label = obj.profile.role_label
            
            colors = {
                'ADMIN': 'bg-red-500',
                'DOCTOR': 'bg-green-500',
                'NURSE': 'bg-blue-400',
                'PATIENT': 'bg-gray-500',
                'MANAGER': 'bg-orange-500',
                'COORDINATOR': 'bg-purple-500'
            }
            color_class = colors.get(role, 'bg-gray-500')
            
            # Contenedor principal con flexbox
            html = '<div class="flex items-center gap-2">'
            
            # Badge del rol con label
            html += format_html(
                '<span class="{} text-white text-xs px-2.5 py-0.5 rounded-full font-medium">'
                '{}</span>',
                color_class, role_label
            )
            
            # Indicador de usuario actual
            if is_current_user:
                html += format_html(
                    '<span class="bg-blue-100 text-blue-800 text-xs px-2 py-0.5 '
                    'rounded-full font-medium flex items-center gap-1">'
                    '<span class="text-xs">👤</span> Tú'
                    '</span>'
                )
            
            html += '</div>'
            return format_html(html)
            
        except Exception as e:
            import traceback
            print(f"Error en get_role_badge: {str(e)}")
            print(traceback.format_exc())
            return format_html(
                '<span class="text-red-500 text-xs">{}</span>',
                role_label if 'role_label' in locals() else 'Error'
            )
    get_role_badge.short_description = "Rol"

    def get_appointment_count(self, obj):
        count = obj.appointments.count()
        upcoming = obj.appointments.filter(date__gte=timezone.now()).count()
        
        return format_html(
            '<div class="flex items-center space-x-2">'
            '<span class="bg-gray-100 text-gray-800 text-xs px-3 py-1 rounded-full">'
            '{} total</span>'
            '{}'
            '</div>',
            count,
            format_html(
                '<span class="bg-blue-100 text-blue-800 text-xs px-3 py-1 rounded-full">'
                '{} próximas</span>',
                upcoming
            ) if upcoming else ''
        )
    get_appointment_count.short_description = "Citas"

    class Media:
        css = {
            'all': (
                'https://cdn.tailwindcss.com',
                'admin/css/forms.css',
                'admin/css/widgets.css',
            )
        }
        js = (
            'admin/js/core.js',
            'admin/js/vendor/jquery/jquery.js',
            'admin/js/jquery.init.js',
        )
