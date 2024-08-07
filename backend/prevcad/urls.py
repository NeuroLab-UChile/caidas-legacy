from django.urls import path, include

from prevcad.views import HealthCategoryView, TextRecomendationsView
from rest_framework import routers

router = routers.DefaultRouter(trailing_slash=False)

router.register('prevcad/health_categories/', HealthCategoryView)
router.register('prevcad/text_recommendations/', TextRecomendationsView)

urlpatterns = [
    path('', include(router.urls)),

    path('health_categories/', HealthCategoryView.as_view({'get': 'list'})),
    path('text_recommendations/', TextRecomendationsView.as_view({'get': 'list'})),
]
