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
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {
            'fields': (
                'first_name',
                'last_name',
                'email',
            ),
            'classes': ('wide',)
        }),
        ('Permisos', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
            'classes': ('collapse',)
        }),
    )

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
                'admin/css/custom_admin.css',
                'admin/css/forms.css',
                'admin/css/widgets.css',
                'admin/css/calendar.css',
                'admin/css/DateTimeShortcuts.css',
            )

        }
        js = (
            'admin/js/calendar.js',
            'admin/js/admin/DateTimeShortcuts.js',
        )

# Registrar el admin personalizado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
