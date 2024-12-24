from django import forms
from .models import Appointment
from .widgets import WeekPickerWidget

class AppointmentForm(forms.ModelForm):
    date = forms.DateField(
        widget=WeekPickerWidget(),
        help_text="Seleccione la semana de la cita"
    )

    class Meta:
        model = Appointment
        fields = '__all__' 