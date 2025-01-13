from rest_framework import routers
from django.urls import path, include
from prevcad.models import HealthCategory

from prevcad.views.profiles import getProfile, uploadProfileImage, deleteProfileImage
from prevcad.views.text_recomendations import TextRecomendationsView
from prevcad.views.health_categories import HealthCategoryListView, save_evaluation_responses, create_health_category, update_health_category
from django.conf import settings
from django.conf.urls.static import static
from .views import admin_views
from .views.appointment_view import AppointmentViewSet
from .views.admin_views import update_training_form


router = routers.DefaultRouter(trailing_slash=False)

router.register('prevcad/text_recommendations/', TextRecomendationsView, basename='text_recommendations')
router.register('prevcad/text_recommendations/<int:pk>/register_click', TextRecomendationsView, basename='recommendation-register-click')

router.register('prevcad/appointments/', AppointmentViewSet, basename='appointments')
# Rutas de la API
urlpatterns = [
  path('prevcad/', include(router.urls)),
  path('', include(router.urls)),
  path('prevcad/user/profile/', getProfile, name='get_profile'),
  path('prevcad/user/profile/upload_image/', uploadProfileImage, name='upload_profile_image'),
  path('prevcad/user/profile/delete_image/', deleteProfileImage, name='delete_profile_image'),
  path('prevcad/health_categories/', HealthCategoryListView.as_view(), name='health-categories'),
  path('prevcad/health-categories/<int:category_id>/responses/', save_evaluation_responses, name='save_responses'),
  path('prevcad/text_recommendations/<int:pk>/register_click', TextRecomendationsView.as_view({'post': 'register_click'}), name='recommendation-register-click'),
  path('prevcad/health-categories/create', 
       create_health_category, 
       name='create_health_category'),
  path('prevcad/health-categories/<int:category_id>/update', 
       update_health_category, 
       name='update_health_category'),
  path('admin/update-evaluation-form/<int:template_id>/', admin_views.update_evaluation_form, name='update_evaluation_form'),
  path('admin/update-training-form/<int:template_id>/', admin_views.update_training_form, name='update_training_form'),
  path('admin/prevcad/healthcategory/<int:object_id>/update_recommendation/', 
       admin_views.update_recommendation, 
       name='update_recommendation'),
  path('admin/prevcad/healthcategory/<int:category_id>/save-professional-evaluation/',
       admin_views.save_professional_evaluation,
       name='admin_save_professional_evaluation'),

  path('admin/categorytemplate/<int:template_id>/update_training_form/', 
       update_training_form, 
       name='update_training_form'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
