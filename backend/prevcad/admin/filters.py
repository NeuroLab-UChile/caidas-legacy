from django.contrib.admin import SimpleListFilter
from ..models import HealthCategory, CategoryTemplate
from django.utils.translation import gettext_lazy as _

class HealthStatusFilter(SimpleListFilter):
    title = 'Estado'
    parameter_name = 'status_color'

    def has_doctor_permission(self, request):
        return request.user.is_authenticated and (
            request.user.groups.filter(name='DOCTOR').exists() or 
            request.user.is_superuser
        )

    def lookups(self, request, model_admin):
        # Solo mostrar opciones si es doctor
        if self.has_doctor_permission(request):
            return HealthCategory.COLOR_CHOICES
        return None

    def queryset(self, request, queryset):
        # Solo filtrar si es doctor y hay un valor seleccionado
        if self.has_doctor_permission(request) and self.value():
            return queryset.filter(status_color=self.value())
        return queryset

    def has_view_permission(self, request):
        return self.has_doctor_permission(request)

class CategoryTypeFilter(SimpleListFilter):
    title = _('Tipo de Evaluación')
    parameter_name = 'evaluation_type'

    EVALUATION_TYPE_CHOICES = [
        ('SELF', 'Auto-evaluación'),
        ('PROFESSIONAL', 'Evaluación Profesional'),
    ]

    def has_admin_permission(self, request):
        return request.user.is_authenticated and (
            request.user.groups.filter(name='DOCTOR').exists() or 
            request.user.is_superuser
        )       

    def lookups(self, request, model_admin):
        if self.has_admin_permission(request):
            return self.EVALUATION_TYPE_CHOICES
        return None

    def queryset(self, request, queryset):
        if self.has_admin_permission(request) and self.value():
            return queryset.filter(evaluation_type=self.value())
        return queryset

    def has_view_permission(self, request):
        return self.has_admin_permission(request) 