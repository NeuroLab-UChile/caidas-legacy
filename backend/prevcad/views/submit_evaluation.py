from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from models import HealthCategory

class SubmitEvaluation(APIView):
    def post(self, request, health_category_id, format=None):
        # Recibimos las respuestas del frontend
        responses = request.data.get('responses', {})

        try:
            health_category = HealthCategory.objects.get(id=health_category_id)
            # Actualizamos las respuestas en el HealthCategory
            health_category.update_evaluation(responses)
            return Response({'status': 'evaluation updated successfully'}, status=200)
        except HealthCategory.DoesNotExist:
            raise ValidationError('HealthCategory not found')
        except ValueError as e:
            raise ValidationError(str(e))
