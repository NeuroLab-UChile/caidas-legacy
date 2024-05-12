from django.contrib import admin

from .models import Admin, Customer, HealthCategory, WorkRecomendation


admin.site.register(Admin)
admin.site.register(Customer)
admin.site.register(WorkRecomendation)
admin.site.register(HealthCategory)


