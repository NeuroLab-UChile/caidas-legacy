from django.urls import path, include

from prevcad.views import HealthCategoryView
from rest_framework import routers

router = routers.DefaultRouter(trailing_slash=False)
router.register('prevcad', HealthCategoryView)

urlpatterns = [
    path('', include(router.urls))
]
