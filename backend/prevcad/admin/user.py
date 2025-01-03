from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django import forms
from ..models import UserProfile, Appointment, HealthCategory

class AppointmentInlineForm(forms.ModelForm):
    date = forms.DateField(
        widget=admin.widgets.AdminDateWidget(),
        help_text="Seleccione la fecha de la cita"
    )

    class Meta:
        model = Appointment
        fields = ['title', 'date', 'description']

class AppointmentInline(admin.TabularInline):
    model = Appointment
    form = AppointmentInlineForm
    extra = 1
    template = 'admin/appointment/edit_inline/tabular.html'
    fields = ('title', 'date', 'description')
    
    class Media:
        css = {
            'all': ('admin/css/forms.css', 'admin/css/widgets.css')
        }
        js = ('admin/js/calendar.js', 'admin/js/admin/DateTimeShortcuts.js')

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'

class HealthCategoryInline(admin.TabularInline):
    model = HealthCategory
    fk_name = 'user'
    extra = 0
    readonly_fields = ['template']
    can_delete = True
    verbose_name_plural = 'Health Categories'
    parent_model = UserProfile

class CustomUserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline, AppointmentInline]
    list_display = (
        'username', 
        'get_role',
        'email', 
        'is_active', 
        
        'get_appointment_count'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__role')
    search_fields = ('username', 'first_name', 'last_name', 'email')

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

    def get_role(self, obj):
        try:
            return obj.profile.get_role_display()
        except (UserProfile.DoesNotExist, AttributeError):
            return 'Sin perfil'
    get_role.short_description = 'Rol'

    def get_appointment_count(self, obj):
        return obj.appointments.count()
    get_appointment_count.short_description = 'Citas'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        UserProfile.objects.get_or_create(user=obj)

    class Media:
        css = {
            'all': ('admin/css/forms.css', 'admin/css/widgets.css')
        }
        js = ('admin/js/calendar.js', 'admin/js/admin/DateTimeShortcuts.js')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    inlines = [HealthCategoryInline]
    list_display = ('user', 'role', 'phone')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'phone')

# Desregistrar el UserAdmin por defecto y registrar el CustomUserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)