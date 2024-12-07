from django.db import models


class ActivityNode(models.Model):
  class NodeType(models.TextChoices):
    CATEGORY_DESCRIPTION = 'CATEGORY_DESCRIPTION', 'Category Description'
    TEXT_QUESTION = 'TEXT_QUESTION', 'Text Question'
    SINGLE_CHOICE_QUESTION = 'SINGLE_CHOICE_QUESTION', 'Single Choice Question'
    MULTIPLE_CHOICE_QUESTION = 'MULTIPLE_CHOICE_QUESTION', 'Multiple Choice Question'
    SCALE_QUESTION = 'SCALE_QUESTION', 'Scale Question'
    IMAGE_QUESTION = 'IMAGE_QUESTION', 'Image Question'

  type = models.TextField(choices=NodeType.choices)

  class Meta:
    abstract = True

class ActivityNodeDescription(ActivityNode):
  description = models.TextField() # proveniente desde los inicios de los tiempos (template)
  image = models.ImageField(upload_to='activity_node_descriptions/', null=True, blank=True)
  first_button_text = models.TextField(null=True, blank=True)
  second_button_text = models.TextField(null=True, blank=True)
  first_button_node_id = models.IntegerField(null=True, blank=True)
  second_button_node_id = models.IntegerField(null=True, blank=True)

class ActivityNodeQuestion(ActivityNode):
  prev_node_id = models.IntegerField(null=True, blank=True)
  next_node_id = models.IntegerField(null=True, blank=True)
  question = models.TextField()
  options = models.JSONField()
  response = models.JSONField()

class TextQuestion(ActivityNodeQuestion):
  pass

class SingleChoiceQuestion(ActivityNodeQuestion):
  pass

class MultipleChoiceQuestion(ActivityNodeQuestion):
  pass

class ScaleQuestion(ActivityNodeQuestion):
  pass

class ImageQuestion(ActivityNodeQuestion):
  pass


