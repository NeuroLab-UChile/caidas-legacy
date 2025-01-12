from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from ..models import UserProfile, Appointment
from django.utils import timezone

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

class CustomUserAdmin(BaseUserAdmin):
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
        role = obj.groups.first().name if obj.groups.exists() else 'Sin rol'
        colors = {
            'ADMIN': 'bg-red-500',
            'DOCTOR': 'bg-green-500',
            'NURSE': 'bg-blue-400',
            'PATIENT': 'bg-gray-500',
            'MANAGER': 'bg-orange-500',
            'COORDINATOR': 'bg-purple-500'
        }
        color_class = colors.get(role, 'bg-gray-500')
        return format_html(
            '<span class="{} text-white text-xs px-3 py-1 rounded-full font-semibold">'
            '{}</span>',
            color_class, role
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

# Registrar el admin personalizado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
