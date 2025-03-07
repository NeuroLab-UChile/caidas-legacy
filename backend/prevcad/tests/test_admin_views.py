from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from prevcad.models import CategoryTemplate
import json
import os

class AdminViewsTest(TestCase):
    def setUp(self):
        # Crear usuario admin
        User = get_user_model()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpass123'
        )
        self.client = Client()
        self.client.login(username='admin', password='adminpass123')

        # Crear template de categoría
        self.category_template = CategoryTemplate.objects.create(
            name='Test Template',
            evaluation_form={'question_nodes': []},
            training_form={'training_nodes': []}
        )

    def test_update_training_form_with_media(self):
        # Crear archivo de prueba
        video_content = b'fake video content'
        video = SimpleUploadedFile(
            "test_video.mp4",
            video_content,
            content_type="video/mp4"
        )

        # Datos del formulario
        training_nodes = [{
            'id': '1',
            'type': 'VIDEO',
            'content': 'Test video content',
            'media_pending': True
        }]

        data = {
            'training_form': json.dumps({'training_nodes': training_nodes}),
            'media_file': video
        }

        # Hacer la petición
        url = reverse('update_training_form', args=[self.category_template.id])
        response = self.client.post(url, data, format='multipart')

        # Verificar respuesta
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')

        # Verificar que el archivo se guardó
        self.category_template.refresh_from_db()
        updated_nodes = self.category_template.training_form['training_nodes']
        self.assertEqual(len(updated_nodes), 1)
        self.assertTrue('media_url' in updated_nodes[0])
        self.assertFalse(updated_nodes[0].get('media_pending', False))

    def test_update_evaluation_form(self):
        # Datos de prueba
        question_nodes = [{
            'id': '1',
            'type': 'MULTIPLE_CHOICE_QUESTION',
            'question': 'Test question',
            'options': ['Option 1', 'Option 2']
        }]

        data = {
            'evaluation_form': json.dumps({'question_nodes': question_nodes})
        }

        # Hacer la petición
        url = reverse('update_evaluation_form', args=[self.category_template.id])
        response = self.client.post(url, data)

        # Verificar respuesta
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')

        # Verificar que los datos se guardaron
        self.category_template.refresh_from_db()
        self.assertEqual(
            self.category_template.evaluation_form['question_nodes'][0]['question'],
            'Test question'
        )

    def tearDown(self):
        # Limpiar archivos subidos
        if hasattr(self.category_template, 'training_form'):
            for node in self.category_template.training_form.get('training_nodes', []):
                if 'media_url' in node:
                    file_path = os.path.join(settings.MEDIA_ROOT, node['media_url'])
                    if os.path.exists(file_path):
                        os.remove(file_path) 