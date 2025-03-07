from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from rest_framework.test import APITestCase
from urllib.parse import urljoin, urlparse
from django.conf import settings
import json
import os
import shutil
from scripts.populate_health_categories import populate_category_templates_from_file
from scripts.depopulate_health_categories import depopulate_category_templates

from prevcad.models import CategoryTemplate, HealthCategory, UserProfile
from prevcad.views.health_categories import HealthCategoryListView

class HealthCategoryUrlsTestCase(APITestCase):
    """Tests para verificar las URLs en HealthCategoryListView"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print("\n=== Iniciando Tests de HealthCategory ===")
        json_path = os.path.join(settings.BASE_DIR, 'scripts', 'generated_categories.json')
        print(f"\n📥 Poblando base de datos desde {json_path}")
        populate_category_templates_from_file(json_path)

    @classmethod
    def tearDownClass(cls):
        print("\n🧹 Limpiando base de datos...")
        depopulate_category_templates()
        media_dirs = ['training_videos', 'training_images', 'category_icons']
        for dir_name in media_dirs:
            dir_path = os.path.join(settings.MEDIA_ROOT, dir_name)
            if os.path.exists(dir_path):
                print(f"🗑️  Limpiando directorio: {dir_name}")
                shutil.rmtree(dir_path)
        super().tearDownClass()

    def setUp(self):
        """Configuración para cada test individual"""
        # Crear usuario de prueba
        self.user = get_user_model().objects.create_user(
            username=f'testuser_{os.urandom(8).hex()}',  # Nombre único
            email='test@example.com',
            password='testpass123'
        )
        
        # Crear o obtener perfil de usuario
        self.user_profile, created = UserProfile.objects.get_or_create(user=self.user)
        
        self.client.force_authenticate(user=self.user)
        self.factory = RequestFactory()
        self.base_url = getattr(settings, 'BASE_URL', 'https://caidas.uchile.cl')

        # Crear HealthCategory para cada template
        for template in CategoryTemplate.objects.all():
            HealthCategory.objects.get_or_create(
                user=self.user_profile,
                template=template,
                defaults={'evaluation_form': template.evaluation_form}
            )

    def tearDown(self):
        """Limpieza después de cada test individual"""
        # Eliminar el usuario y su perfil
        if hasattr(self, 'user'):
            self.user.delete()  # Esto también eliminará el perfil y las categorías asociadas

    def verify_media_url(self, url, expected_prefix=None, node_type=None, check_https=True):
        """Verifica que una URL de media venga con HTTPS directamente de la vista"""
        if not url:
            return False, "URL vacía"

        # La URL debe ser absoluta y HTTPS desde la vista
        if not url.startswith('https://'):
            return False, f"URL debe ser absoluta y HTTPS: {url}"

        parsed_url = urlparse(url)
        
        # Verificar dominio correcto
        expected_domain = urlparse(self.base_url).netloc
        if parsed_url.netloc != expected_domain:
            return False, f"Dominio incorrecto. Esperado: {expected_domain}, Recibido: {parsed_url.netloc}"

        # Verificar prefijo según tipo de nodo
        path = parsed_url.path.lstrip('/')
        if path.startswith('media/'):
            path = path[6:]  # Remover 'media/'

        if node_type == 'VIDEO_NODE':
            if not path.startswith('training_videos/'):
                return False, f"URL de video inválida: {url}"
        elif node_type in ['IMAGE_NODE', 'DESCRIPTION_NODE']:
            if not path.startswith('training_images/'):
                return False, f"URL de imagen inválida: {url}"
        elif expected_prefix and not path.startswith(expected_prefix):
            return False, f"URL debe comenzar con '{expected_prefix}'"

        # Verificar que el archivo existe localmente
        file_path = os.path.join(settings.MEDIA_ROOT, path)
        if not os.path.exists(file_path):
            return False, f"Archivo no encontrado: {file_path}"
            
        return True, "URL válida con HTTPS y archivo existente"

    def test_health_category_list_view_structure(self):
        """Verifica la estructura básica de la respuesta"""
        request = self.factory.get('/api/health-categories/')
        request.user = self.user
        view = HealthCategoryListView.as_view()
        response = view(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        
        required_fields = [
            'id', 'name', 'icon', 'description', 'evaluation_type',
            'evaluation_form', 'status', 'recommendations', 'training_form'
        ]
        
        for category in response.data:
            for field in required_fields:
                self.assertIn(field, category, f"Campo '{field}' no encontrado")
            
            # Verificar estructura de training_form
            if category.get('training_form'):
                self.assertIn('training_nodes', category['training_form'])
                for node in category['training_form']['training_nodes']:
                    if node.get('media_url'):
                        self.assertTrue(
                            node['media_url'].startswith('https://'),
                            f"Media URL debe ser absoluta y HTTPS: {node['media_url']}"
                        )

    def test_health_category_media_urls(self):
        """Verifica que todas las URLs de media sean HTTPS y accesibles"""
        request = self.factory.get('/api/health-categories/')
        request.user = self.user
        view = HealthCategoryListView.as_view()
        response = view(request)
        
        categories = response.data
        print(f"\n🔍 Verificando {len(categories)} categorías")
        
        for category in categories:
            print(f"\n📁 Categoría: {category.get('name', 'Sin nombre')}")
            
            # Verificar icono
            if 'icon' in category and category['icon']:
                is_valid, message = self.verify_media_url(
                    category['icon'],
                    'category_icons',
                    check_https=True
                )
                self.assertTrue(
                    is_valid,
                    f"Icono inválido en categoría {category.get('name')}: {message}"
                )
                print(f"  └─ Icono: {category['icon']} ({message})")
            
            # Verificar training_form
            if 'training_form' in category and category['training_form']:
                training_form = category['training_form']
                if 'training_nodes' in training_form:
                    print(f"  └─ Nodos de entrenamiento: {len(training_form['training_nodes'])}")
                    for node in training_form['training_nodes']:
                        print(f"    ├─ Nodo {node.get('id')}: {node.get('type')}")
                        if 'media_url' in node and node['media_url']:
                            is_valid, message = self.verify_media_url(
                                node['media_url'],
                                node_type=node['type'],
                                check_https=True
                            )
                            self.assertTrue(
                                is_valid,
                                f"Media URL inválida en nodo {node.get('id')}: {message}"
                            )
                            print(f"      └─ Media: {node['media_url']} ({message})")

            # Verificar evaluation_form
            if 'evaluation_form' in category and category['evaluation_form']:
                print("  └─ Verificando formulario de evaluación")
                eval_form = category['evaluation_form']
                if 'responses' in eval_form:
                    for node_id, response in eval_form['responses'].items():
                        if isinstance(response, dict) and 'answer' in response:
                            if 'images' in response['answer']:
                                for img in response['answer']['images']:
                                    is_valid, message = self.verify_media_url(
                                        img['url'],
                                        'evaluation_images',
                                        check_https=True
                                    )
                                    self.assertTrue(
                                        is_valid,
                                        f"URL de imagen inválida en evaluación: {message}"
                                    )
                                    print(f"    └─ Imagen: {img['url']} ({message})")

if __name__ == '__main__':
    print("Iniciando tests de HealthCategory...")
