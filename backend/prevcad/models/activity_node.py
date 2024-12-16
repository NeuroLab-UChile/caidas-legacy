from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


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
    )

    @property
    def next_node_id(self):
        """Retorna el ID del siguiente nodo en la secuencia"""
        if hasattr(self, '_next_node_id'):
            return self._next_node_id
        return None

    @next_node_id.setter
    def next_node_id(self, value):
        self._next_node_id = value

    class Meta:
        abstract = True


class ActivityNodeDescription(ActivityNode):
    description = models.TextField()
    image = models.ImageField(upload_to='activity_node_descriptions/', null=True, blank=True)
    first_button_text = models.TextField(null=True, blank=True)
    second_button_text = models.TextField(null=True, blank=True)
    first_button_node_id = models.IntegerField(null=True, blank=True)
    second_button_node_id = models.IntegerField(null=True, blank=True)

    # Add these fields for the generic foreign key
    next_node_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+'
    )
    next_node_object_id = models.PositiveIntegerField(null=True, blank=True)
    next_node = GenericForeignKey('next_node_content_type', 'next_node_object_id')


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
