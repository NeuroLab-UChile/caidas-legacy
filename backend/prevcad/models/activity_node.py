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
        RESULT_NODE = 'RESULT_NODE', 'Result Node',
        WEEKLY_RECIPE_NODE = 'WEEKLY_RECIPE_NODE', 'Weekly Recipe Node'
        VIDEO_NODE = 'VIDEO_NODE', 'Video Node'
        TEXT_NODE = 'TEXT_NODE', 'Text Node'
        IMAGE_NODE = 'IMAGE_NODE', 'Image Node'


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


class WeeklyRecipeNode(ActivityNode):
    DAYS_OF_WEEK = [
        ('MON', 'Lunes'),
        ('TUE', 'Martes'),
        ('WED', 'Miércoles'),
        ('THU', 'Jueves'),
        ('FRI', 'Viernes'),
        ('SAT', 'Sábado'),
        ('SUN', 'Domingo')
    ]

    MEAL_TYPES = [
        ('BREAKFAST', 'Desayuno'),
        ('LUNCH', 'Almuerzo'),
        ('DINNER', 'Cena')
    ]

    title = models.CharField(max_length=200, default="Plan Semanal WeTrain")
    description = models.TextField(default="Plan de alimentación personalizado")
    
    weekly_plan = models.JSONField(default=dict, help_text="""
    Estructura esperada:
    {
        "MON": {
            "BREAKFAST": {
                "meal": "1 vaso de leche",
                "proteins": "8g",
                "notes": "Preferiblemente descremada"
            },
            "LUNCH": {...},
            "DINNER": {...}
        },
        "TUE": {...},
        ...
    }
    """)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = "Plan Semanal"
        verbose_name_plural = "Planes Semanales"

    def get_day_meals(self, day_code):
        """Obtiene las comidas para un día específico"""
        return self.weekly_plan.get(day_code, {})

    def get_meal(self, day_code, meal_type):
        """Obtiene una comida específica de un día"""
        day_meals = self.get_day_meals(day_code)
        return day_meals.get(meal_type, {})



class VideoNode(ActivityNode):
    content = models.FileField(upload_to='videos/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)


class TextNode(ActivityNode):
    content = models.TextField(null=True, blank=True)


class ImageNode(ActivityNode):
    content = models.ImageField(upload_to='images/', null=True, blank=True)
 

