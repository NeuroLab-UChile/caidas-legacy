from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework.response import Response
from prevcad.models import (
  TextRecomendation,
  UserRecommendationInteraction,
)
from prevcad.serializers.text_recomendation_serializer import (
  TextRecomendationSerializer,
)
from django.db.models import F, Exists, OuterRef, Q, Count, Max, Case, When
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
import logging
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import Coalesce
from django.db import models

logger = logging.getLogger(__name__)


class TextRecomendationsView(viewsets.ModelViewSet):
  queryset = TextRecomendation.objects.all()
  serializer_class = TextRecomendationSerializer
  permission_classes = [IsAuthenticated]

  def create(self, request: Request, *args, **kwargs) -> Response:
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    self.perform_create(serializer)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

  def retrieve(self, request: Request, pk=None, *args, **kwargs) -> Response:
    try:
      instance = self.get_object()
      serializer = self.get_serializer(instance)
      return Response(serializer.data)
    except TextRecomendation.DoesNotExist:
      return Response(status=status.HTTP_404_NOT_FOUND)

  def list(self, request, *args, **kwargs):
    try:
        user = request.user
        logger.info(f"Getting recommendations for user {user.id}")
        
        # Obtener las últimas recomendaciones mostradas al usuario
        recent_shown = request.session.get('last_shown_recommendations', [])
        logger.info(f"Previously shown recommendations: {recent_shown}")
        
        # Obtener recomendaciones no vistas y no mostradas recientemente
        recommendations = TextRecomendation.objects.exclude(
            Q(id__in=UserRecommendationInteraction.objects.filter(
                user=user,
                last_clicked__gte=timezone.now() - timedelta(hours=24)
            ).values_list('recommendation_id', flat=True)) |
            Q(id__in=recent_shown)
        ).order_by('?')[:10]
        
        if recommendations.count() < 10:
            logger.info("Not enough fresh recommendations, adding older ones")
            # Obtener recomendaciones vistas hace más tiempo, excluyendo las recientes
            older_viewed = TextRecomendation.objects.filter(
                userrecommendationinteraction__user=user
            ).exclude(
                id__in=recent_shown
            ).annotate(
                last_viewed=Max('userrecommendationinteraction__last_clicked')
            ).order_by('last_viewed')
            
            # Agregar recomendaciones más antiguas hasta completar 10
            needed = 10 - recommendations.count()
            recommendations = list(recommendations) + list(older_viewed[:needed])
        
        # Guardar los IDs mostrados en la sesión
        shown_ids = [rec.id for rec in recommendations]
        request.session['last_shown_recommendations'] = shown_ids
        logger.info(f"Storing shown recommendations: {shown_ids}")
        
        # Ordenar por categorías preferidas del usuario
        favorite_categories = UserRecommendationInteraction.objects.filter(
            user=user
        ).values('recommendation__category').annotate(
            total_clicks=Count('id')
        ).order_by('-total_clicks')
        
        category_order = {
            cat['recommendation__category']: index 
            for index, cat in enumerate(favorite_categories)
        }
        
        # Ordenar recomendaciones por categorías preferidas
        recommendations = sorted(
            recommendations,
            key=lambda x: category_order.get(x.category, float('inf'))
        )
        
        serializer = self.get_serializer(recommendations, many=True)
        return Response({
            'recommendations': serializer.data,
            'count': len(recommendations),
            'session_id': request.session.session_key  # Para debugging
        })
        
    except Exception as e:
        logger.error(f"Error in list view: {str(e)}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

  @action(detail=True, methods=['post'])
  def register_click(self, request, pk=None):
    try:
      user = request.user
      recommendation = self.get_object()
      category = recommendation.category
      
      # Registrar la interacción
      interaction, created = UserRecommendationInteraction.objects.get_or_create(
        user=user,
        recommendation=recommendation,
        defaults={'clicks': 1}
      )
      
      if not created:
        interaction.clicks = F('clicks') + 1
        interaction.last_clicked = timezone.now()
        interaction.save()
        interaction.refresh_from_db()
      
      # Obtener recomendaciones relacionadas no vistas
      viewed_ids = UserRecommendationInteraction.objects.filter(
        user=user
      ).values_list('recommendation_id', flat=True)
      
      related_recommendations = TextRecomendation.objects.filter(
        category=category
      ).exclude(
        id__in=viewed_ids
      ).exclude(
        id=recommendation.id
      ).order_by('?')[:5]  # Máximo 5 recomendaciones relacionadas
      
      # Si no hay suficientes no vistas, agregar algunas vistas hace tiempo
      if related_recommendations.count() < 5:
        viewed_related = TextRecomendation.objects.filter(
          category=category,
          id__in=viewed_ids
        ).exclude(
          id=recommendation.id
        ).annotate(
          last_viewed=Max('userrecommendationinteraction__last_clicked')
        ).order_by('last_viewed')[:3]  # Agregar hasta 3 vistas
        
        related_recommendations = list(related_recommendations) + list(viewed_related)
      
      logger.info(f"Returning {len(related_recommendations)} related recommendations")
      serializer = self.get_serializer(related_recommendations, many=True)
      
      return Response({
        'clicked_recommendation': self.get_serializer(recommendation).data,
        'more_recommendations': serializer.data,
        'category': category,
        'interaction': {
          'clicks': interaction.clicks,
          'last_clicked': interaction.last_clicked
        }
      })
      
    except Exception as e:
      logger.error(f"Error in register_click: {str(e)}", exc_info=True)
      return Response(
        {'error': str(e)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )
