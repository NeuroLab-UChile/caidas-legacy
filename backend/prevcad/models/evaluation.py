from django.db import models
from django.utils import timezone

class QuestionNode(models.Model):
    evaluation_form = models.ForeignKey(
        'EvaluationForm',
        on_delete=models.CASCADE,
        related_name='nodes'
    )
    type = models.CharField(max_length=50)
    question = models.TextField()
    options = models.JSONField(null=True, blank=True)
    required = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

class EvaluationForm(models.Model):
    health_category = models.OneToOneField(
        'HealthCategory', 
        on_delete=models.CASCADE,
        related_name='evaluation_form'
    )
    responses = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        help_text="Respuestas del usuario"
    )
    professional_responses = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        help_text="Respuestas del profesional"
    )
    completed_date = models.DateTimeField(
        null=True,
        blank=True
    )
    is_draft = models.BooleanField(
        default=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    question_nodes = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'prevcad_evaluation_form'

    def __str__(self):
        return f"Evaluación para {self.health_category}"

    def get_or_create_question_nodes(self):
        """Obtiene o crea los nodos de preguntas para la evaluación"""
        if not self.question_nodes:
            return []

        try:
            nodes = []
            for node_data in self.question_nodes:
                # Debug para ver la estructura de los datos
                print("DEBUG - Node data:", node_data)
                
                # Verificar que tengamos los datos necesarios
                if not isinstance(node_data, dict):
                    print(f"WARNING: node_data no es un diccionario: {node_data}")
                    continue

                # Obtener los campos con valores por defecto si no existen
                question = node_data.get('question', node_data.get('label', ''))
                options = node_data.get('options', [])
                node_type = node_data.get('type', 'question')
                node_id = node_data.get('id')

                node = {
                    'id': node_id,
                    'type': node_type,
                    'question': question,
                    'options': options
                }
                nodes.append(node)

            return nodes
        except Exception as e:
            print(f"Error procesando nodos de preguntas: {str(e)}")
            print(f"question_nodes: {self.question_nodes}")
            return []

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Crear nodos de preguntas al crear el formulario
            self.get_or_create_question_nodes() 

    def save_professional_response(self, data):
        """
        Guarda una respuesta profesional con el formato correcto
        """
        self.professional_responses = {
            'observations': data.get('observations', ''),
            'diagnosis': data.get('diagnosis', ''),
            'professional_name': data.get('professional_name', ''),
            'evaluation_date': timezone.now().isoformat()
        }
        self.completed_date = timezone.now()
        self.is_draft = False
        self.save()

    def get_professional_response(self):
        """
        Obtiene la respuesta profesional formateada
        """
        if not self.professional_responses:
            return None
        
        return {
            'observations': self.professional_responses.get('observations', ''),
            'diagnosis': self.professional_responses.get('diagnosis', ''),
            'professional_name': self.professional_responses.get('professional_name', ''),
            'evaluation_date': self.completed_date
        } 