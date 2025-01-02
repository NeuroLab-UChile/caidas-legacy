from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import HealthCategory, CategoryTemplate, ActivityNode, UserProfile
from ..serializers import HealthCategorySerializer
from rest_framework.decorators import api_view
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from datetime import datetime
import json
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from prevcad.models import UserProfile

class HealthCategoryListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        print("=== Debug HealthCategoryListView ===")
        print(f"Usuario autenticado: {request.user.username}")
        
        user_profile = get_object_or_404(UserProfile, user=request.user)
        categories = HealthCategory.objects.filter(user__user=request.user)
        
        serialized_categories = []
        
        for category in categories:
            template = category.template
            if template:
                # Usar el serializer en lugar de construir el diccionario manualmente
                serializer = HealthCategorySerializer(category)
                serialized_categories.append(serializer.data)
        
        return Response(serialized_categories)

@api_view(['POST'])
def save_evaluation_responses(request, category_id):
    print("\n=== Debug save_evaluation_responses ===")
    print(f"Request data: {request.data}")
    
    try:
        # Primero obtener el perfil del usuario
        user_profile = get_object_or_404(UserProfile, user=request.user)
        
        # Luego buscar la categoría asegurándose que pertenece al usuario
        health_category = get_object_or_404(
            HealthCategory, 
            id=category_id, 
            user=user_profile
        )
        
        # Obtener o crear el formulario de evaluación
        evaluation_form = health_category.evaluation_form
        
        # Actualizar las respuestas
        responses = request.data.get('responses', {})
        if evaluation_form.responses is None:
            evaluation_form.responses = {}
            
        evaluation_form.responses.update(responses)
        
        # Si hay respuestas, actualizar la fecha de completado
        if responses:
            evaluation_form.completed_date = timezone.now()
            
        evaluation_form.save()
        
        return Response({
            'status': 'success',
            'message': 'Respuestas guardadas correctamente'
        })
            
    except HealthCategory.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Categoría de salud no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error saving responses: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def update_health_category(request, category_id):
    try:
        user_profile = get_object_or_404(UserProfile, user=request.user)
        category = get_object_or_404(
            HealthCategory, 
            id=category_id, 
            user=user_profile
        )
        
        # Agregar el usuario que actualiza
        data = request.data.copy()
        data['updated_by'] = request.user.get_full_name()
        
        if category.update(data):
            return Response({
                'status': 'success',
                'message': 'Categoría actualizada correctamente',
                'data': HealthCategorySerializer(category).data
            })
        else:
            return Response({
                'status': 'error',
                'message': 'Error al actualizar la categoría'
            }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['PUT'])
def update_category_template(request, template_id):
    try:
        template = CategoryTemplate.objects.get(id=template_id)
        template.name = request.data.get('name', template.name)
        template.description = request.data.get('description', template.description)
        template.evaluation_form = request.data.get('evaluation_form', template.evaluation_form)
        template.save()
        return Response({'status': 'success'})
    except CategoryTemplate.DoesNotExist:
        return Response({'error': 'Template not found'}, status=404)




@api_view(['POST'])
def create_health_category(request):
    try:
        print("Recibiendo request para crear health category:", request.data)
        
        template_id = request.data.get('template_id')
        if not template_id:
            return Response({
                'status': 'error',
                'message': 'template_id es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener o crear el perfil del usuario
        user_profile = get_object_or_404(UserProfile, user=request.user)
        template = get_object_or_404(CategoryTemplate, id=template_id)
            
        # Verificar si ya existe una categoría
        existing_category = HealthCategory.objects.filter(
            user=user_profile,
            template=template
        ).first()
        
        if existing_category:
            serializer = HealthCategorySerializer(existing_category)
            return Response({
                'status': 'success',
                'message': 'Ya existe una evaluación para este usuario y template',
                'data': serializer.data
            })
            
        # Crear nueva categoría con el perfil del usuario
        health_category = HealthCategory.objects.create(
            user=user_profile,
            template=template,
            evaluation_form=template.evaluation_form
        )
        
        serializer = HealthCategorySerializer(health_category)
        return Response({
            'status': 'success',
            'message': 'Categoría creada exitosamente',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"Error al crear health category: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_health_category_detail(request, category_id):
    try:
        user_profile = get_object_or_404(UserProfile, user=request.user)
        category = get_object_or_404(
            HealthCategory, 
            id=category_id, 
            user=user_profile
        )
        
        serializer = HealthCategorySerializer(category)
        return Response({
            'status': 'success',
            'data': serializer.data
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

