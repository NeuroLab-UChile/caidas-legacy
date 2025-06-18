from django.contrib import admin
from .category_template import CategoryTemplateAdmin
from .health_category import HealthCategoryAdmin
from .encoders import CustomJSONEncoder
from ..models import CategoryTemplate, HealthCategory
from .filters import HealthStatusFilter

from .appointment import AppointmentAdmin
from .user import CustomUserAdmin
from .action_log import ActionLogAdmin
from ..models import UserProfile
from .text_recommendation import TextRecomendationAdmin
from .app_activity_log import AppActivityLogAdmin