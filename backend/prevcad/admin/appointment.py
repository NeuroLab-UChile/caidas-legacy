from django.contrib import admin
from django import forms
from ..models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'date', 'status', 'created_at')
    list_filter = ('status', 'user')
    search_fields = ('title', 'description', 'user__username')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description')
        }),
        ('Detalles de la Cita', {
            'fields': ('date', 'status', 'user')
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['date'].widget = admin.widgets.AdminSplitDateTime()
        form.base_fields['description'].widget = forms.Textarea(attrs={'rows': 3})
        return form

class AppointmentInline(admin.TabularInline):
    model = Appointment
    extra = 1
    fields = ('title', 'date', 'status', 'description')