from django.db import models
from django.contrib.auth.models import User


class ActivityNode(models.Model):
    class NodeType(models.TextChoices):
        CATEGORY_DESCRIPTION = 'CATEGORY_DESCRIPTION', 'Category Description'
        TEXT_QUESTION = 'TEXT_QUESTION', 'Text Question'
        SINGLE_CHOICE_QUESTION = 'SINGLE_CHOICE_QUESTION', 'Single Choice Question'
        MULTIPLE_CHOICE_QUESTION = 'MULTIPLE_CHOICE_QUESTION', 'Multiple Choice Question'
        SCALE_QUESTION = 'SCALE_QUESTION', 'Scale Question'
        IMAGE_QUESTION = 'IMAGE_QUESTION', 'Image Question'
        RESULT_NODE = 'RESULT_NODE', 'Result Node'

    type = models.TextField(choices=NodeType.choices)
    next_node = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='previous_node',
        help_text="Next node in the sequence"
    )
    

    class Meta:
        abstract = True


class ActivityNodeDescription(ActivityNode):
    description = models.TextField()
    image = models.ImageField(upload_to='activity_node_descriptions/', null=True, blank=True)
    first_button_text = models.TextField(null=True, blank=True)
    second_button_text = models.TextField(null=True, blank=True)
    first_button_node_id = models.IntegerField(null=True, blank=True)
    second_button_node_id = models.IntegerField(null=True, blank=True)


class ActivityNodeQuestion(ActivityNode):
    question = models.TextField()
    image = models.ImageField(upload_to='activity_node_questions/', null=True, blank=True)
    result = models.JSONField(null=True, blank=True)


class TextQuestion(ActivityNodeQuestion):
    pass


class SingleChoiceQuestion(ActivityNodeQuestion):
    options = models.JSONField(blank=True, null=True)


class MultipleChoiceQuestion(ActivityNodeQuestion):
    options = models.JSONField(blank=True, null=True)


class ScaleQuestion(ActivityNodeQuestion):
    min_value = models.IntegerField(blank=True, null=True)
    max_value = models.IntegerField(blank=True, null=True)
    step = models.IntegerField(blank=True, null=True)


class ImageQuestion(ActivityNodeQuestion):
    pass


class ResultNode(ActivityNode):
    response = models.JSONField(null=True, blank=True)
