from django.contrib import admin
from django import forms
from ..models import Appointment



class AppointmentForm(forms.ModelForm):
    date = forms.DateField(
        widget=admin.widgets.AdminDateWidget(),
        help_text="Seleccione la fecha de la cita"
    )
    time = forms.TimeField(
        widget=admin.widgets.AdminTimeWidget(),
        required=False
    )

    class Meta:
        model = Appointment
        fields = ['title', 'date', 'description', 'user']

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

class AppointmentInline(admin.TabularInline):
    model = Appointment
    form = AppointmentForm
    extra = 1
    template = 'admin/appointment/edit_inline/tabular.html'
    fields = ('title', 'date', 'description')
    
    class Media:
        css = {
            'all': ('admin/css/forms.css', 'admin/css/widgets.css')
        }
        js = ('admin/js/calendar.js', 'admin/js/admin/DateTimeShortcuts.js')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    form = AppointmentForm
    list_display = ('title', 'user', 'date', 'created_at')
    list_filter = ('date', 'created_at', 'user')
    search_fields = ('title', 'description', 'user__username')
    date_hierarchy = 'date'
    ordering = ('-date',)
    
    # Especifica los templates personalizados
    change_form_template = 'admin/appointment/change_form.html'
    change_list_template = 'admin/appointment/change_list.html'

    class Media:
        css = {
            'all': ('admin/css/forms.css', 'admin/css/widgets.css')
        }
        js = ('admin/js/calendar.js', 'admin/js/admin/DateTimeShortcuts.js')