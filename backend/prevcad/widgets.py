from django import forms
import datetime

class WeekPickerWidget(forms.TextInput):
    template_name = 'admin/widgets/week_picker.html'

    class Media:
        css = {
            'all': ('admin/css/weekpicker.css',)
        }
        js = ('admin/js/weekpicker.js',)

    def format_value(self, value):
        if isinstance(value, datetime.date):
            year, week, _ = value.isocalendar()
            return f"{year}-W{week:02}"
        return super().format_value(value) 