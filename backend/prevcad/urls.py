from rest_framework import routers
from django.urls import path, include

from prevcad.views.profiles import (
  getProfile,
)
from prevcad.views.health_categories import (
  HealthCategoryView,
)
from prevcad.views.text_recommendations import (
  TextRecomendationsView,
)
from prevcad.views.forms import (
  FormView,
  FormByCategoryTestView,
  LastTestResultsView,
)


router = routers.DefaultRouter(trailing_slash=False)

router.register('prevcad/forms/', FormView)
router.register('prevcad/health_categories/', HealthCategoryView)
router.register('prevcad/text_recommendations/', TextRecomendationsView)

# Rutas de la API
urlpatterns = [
  path('', include(router.urls)),
  path('prevcad/user/profile/', getProfile, name='get_profile'),
  path('prevcad/health_categories/<int:category_id>/test_form/', FormByCategoryTestView.as_view(), name='test_form_by_category'),
  path('prevcad/health_categories/<int:category_id>/last_test_results/', LastTestResultsView.as_view(), name='last_test_results'),
]
