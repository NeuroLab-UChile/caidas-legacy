from rest_framework import routers
from django.urls import path, include

from prevcad.views.profiles import getProfile
from prevcad.views.text_recomendations import TextRecomendationsView
from prevcad.views.health_categories import HealthCategoryListView



router = routers.DefaultRouter(trailing_slash=False)

router.register('prevcad/text_recommendations/', TextRecomendationsView)


# Rutas de la API
urlpatterns = [
  path('', include(router.urls)),
  path('prevcad/user/profile/', getProfile, name='get_profile'),
  path('prevcad/health_categories/', HealthCategoryListView.as_view(), name='health-categories'),

]
