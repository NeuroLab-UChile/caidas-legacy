from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import HealthCategory, EvaluationRecommendation, TextRecomendation, WorkRecommendation, Profile

# Define an inline admin descriptor for Profile model
class ProfileInline(admin.StackedInline):
  model = Profile
  can_delete = False
  verbose_name_plural = 'Profiles'
  fk_name = 'user'

# Extend the existing UserAdmin
class UserAdmin(BaseUserAdmin):
  inlines = [ProfileInline]
  list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active')
  list_filter = ('is_staff', 'is_superuser', 'is_active')

  def get_inline_instances(self, request, obj=None):
    if not obj:
      return list()
    return super(UserAdmin, self).get_inline_instances(request, obj)

# Unregister the original User admin and register the new one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register other models
admin.site.register(HealthCategory)
admin.site.register(EvaluationRecommendation)
admin.site.register(WorkRecommendation)
admin.site.register(TextRecomendation)
