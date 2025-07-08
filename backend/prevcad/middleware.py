from django.conf import settings

class AbsoluteURLMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        if hasattr(response, 'context_data'):
            response.context_data['DOMAIN'] = settings.DOMAIN
        return response 


# https://github.com/mishbahr/django-modeladmin-reorder/issues/47#issuecomment-1141024854

from admin_reorder.middleware import ModelAdminReorder

class ModelAdminReorderWithNav(ModelAdminReorder):
    def process_template_response(self, request, response):
        if (
            getattr(response, "context_data", None)
            and not response.context_data.get("app_list")
            and (available_apps := response.context_data.get("available_apps"))
        ):
            response.context_data["app_list"] = available_apps
            response = super().process_template_response(request, response)
            response.context_data["available_apps"] = response.context_data["app_list"]
            return response

        return super().process_template_response(request, response)
