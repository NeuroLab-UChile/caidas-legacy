from rest_framework import routers
from django.urls import path, include

from prevcad.views import (
  HealthCategoryView, 
  TextRecomendationsView,
  FormView,
  FormByCategoryView,
  getProfile
)

router = routers.DefaultRouter(trailing_slash=False)

router.register('prevcad/forms/', FormView) 
router.register('prevcad/health_categories/', HealthCategoryView)
router.register('prevcad/text_recommendations/', TextRecomendationsView)

# Rutas de la API
urlpatterns = [
  path('', include(router.urls)),
  path('prevcad/health_categories/<int:category_id>/forms/', FormByCategoryView.as_view()),
  path('prevcad/user/profile/', getProfile, name='get_profile'),
]