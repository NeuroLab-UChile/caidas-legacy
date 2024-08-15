from django.urls import path, include
from prevcad.views import HealthCategoryView, TextRecomendationsView
from rest_framework import routers

router = routers.DefaultRouter(trailing_slash=False)

# Registro de las vistas en el enrutador
router.register('prevcad/health_categories/', HealthCategoryView)
router.register('prevcad/text_recommendations/', TextRecomendationsView)

urlpatterns = [
    path('', include(router.urls)),
]
