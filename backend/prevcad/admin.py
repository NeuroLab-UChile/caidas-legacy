from django.contrib import admin # type: ignore
from django.contrib.auth.models import User # type: ignore
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin # type: ignore
from .models import HealthCategory, EvaluationRecommendation, TextRecomendation

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(HealthCategory)
admin.site.register(EvaluationRecommendation)
admin.site.register(TextRecomendation)