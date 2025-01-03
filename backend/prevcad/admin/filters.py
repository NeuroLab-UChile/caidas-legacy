from django.contrib.admin import SimpleListFilter
from ..models import HealthCategory

class HealthStatusFilter(SimpleListFilter):
    title = 'Estado'
    parameter_name = 'status_color'

    def lookups(self, request, model_admin):
        return HealthCategory.COLOR_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status_color=self.value()) 