import base64
from rest_framework import serializers
from django.utils.encoding import smart_str

from prevcad.models import (
  Form,
)




class FormSerializer(serializers.ModelSerializer):
  questions = serializers.SerializerMethodField()

  class Meta:
    model = Form
    fields = ['id', 'title', 'description', 'questions']

  def get_questions(self, obj):
    questions = obj.questions.all()
    return [
      {
        'id': question.id,
        'question_text': question.question_text,
        'question_type': question.question_type,
        'options': question.options
      }
      for question in questions
    ]
