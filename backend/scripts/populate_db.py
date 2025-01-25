import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from prevcad.models import (
  PhysicalActivity,
  TextRecomendation
)

PhysicalActivity.objects.all().delete()
TextRecomendation.objects.all().delete()

print("All records deleted successfully. Tables are now empty.")
