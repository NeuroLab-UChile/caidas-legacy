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