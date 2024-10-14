from django.urls import path, include
from prevcad.views import HealthCategoryView, TextRecomendationsView,getProfile
from rest_framework import routers

router = routers.DefaultRouter(trailing_slash=False)

# Registro de las vistas en el enrutador con basename
router.register('prevcad/health_categories/', HealthCategoryView)
router.register('prevcad/text_recommendations/', TextRecomendationsView,)



urlpatterns = [
  path('', include(router.urls)),
  path('prevcad/user/profile/', getProfile, name='get_profile'),
]
