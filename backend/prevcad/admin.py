from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import (
  TextRecomendation,
  Profile,
  CategoryTemplate,
  HealthCategory
)

# Define an inline admin descriptor for Profile model
class ProfileInline(admin.StackedInline):
  model = Profile
  can_delete = False
  verbose_name_plural = 'Profiles'
  fk_name = 'user'

# Add HealthCategory inline to show categories in user admin
class HealthCategoryInline(admin.TabularInline):
  model = HealthCategory
  extra = 0  # Don't show empty forms
  readonly_fields = ['template', 'name', 'icon']  # Make them read-only
  can_delete = True
  verbose_name_plural = 'Health Categories'

# Extend the existing UserAdmin
class UserAdmin(BaseUserAdmin):
  inlines = [ProfileInline, HealthCategoryInline]  # Add HealthCategoryInline
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
admin.site.register(CategoryTemplate)
admin.site.register(HealthCategory)
admin.site.register(TextRecomendation)

