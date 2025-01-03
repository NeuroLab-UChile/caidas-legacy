from rest_framework import serializers
from ..models import EvaluationForm, QuestionNode, Response

class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = ['id', 'answer', 'created_at', 'updated_at']

class QuestionNodeSerializer(serializers.ModelSerializer):
    responses = ResponseSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuestionNode
        fields = ['id', 'type', 'question', 'options', 'required', 'order', 'responses']

class EvaluationFormSerializer(serializers.ModelSerializer):
    question_nodes = QuestionNodeSerializer(many=True, read_only=True, source='nodes')
    professional_responses = ResponseSerializer(many=True, read_only=True)
    
    class Meta:
        model = EvaluationForm
        fields = ['id', 'form_type', 'completed_date', 'question_nodes', 'professional_responses'] 