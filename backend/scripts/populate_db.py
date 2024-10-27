import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from prevcad.models import HealthCategory, WorkRecommendation, EvaluationRecommendation, TextRecomendation

# Delete all records from the tables
HealthCategory.objects.all().delete()
WorkRecommendation.objects.all().delete()
EvaluationRecommendation.objects.all().delete()
TextRecomendation.objects.all().delete()

print("All records deleted successfully. Tables are now empty.")
