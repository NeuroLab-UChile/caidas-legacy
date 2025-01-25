import { theme } from "@/src/theme";
import { Category } from "../app/types/category";

export const getCategoryStatus = (category: Category) => {
  if (!category?.evaluation_form?.question_nodes) return null;

  const isProEvaluation = category.evaluation_type.type === 'PROFESSIONAL';
  const hasRecommendation = category.recommendations && !category.recommendations.is_draft;
  const isProfessionalReviewed = category.status.professional_reviewed;

  // Evaluación profesional completada y revisada
  if (isProEvaluation && hasRecommendation && isProfessionalReviewed) {
    return {
      status: 'reviewed',
      text: '✅ Evaluación Revisada por Doctor',
      color: category.recommendations.status.color,
      statusText: category.recommendations.status.text
    };
  }

  // Evaluación completada pero pendiente de revisión profesional
  if (category.status.is_completed) {
    return {
      status: 'completed',
      text: isProEvaluation
        ? '⏳ Pendiente de Revisión Médica'
        : '✅ Auto-evaluación Completada',
      color: theme.colors.text,
      statusText: category.status.text
    };
  }

  // Evaluación en progreso
  const totalQuestions = category.evaluation_form.question_nodes.length;
  const answeredQuestions = Object.keys(category.evaluation_form.responses || {}).length;

  if (answeredQuestions > 0) {
    const progress = Math.round((answeredQuestions / totalQuestions) * 100);
    return {
      status: 'in_progress',
      text: `📝 Evaluación en Progreso (${answeredQuestions}/${totalQuestions})`,
      progress,
      color: category.status.color
    };
  }

  // Estado pendiente
  return {
    status: 'pending',
    text: isProEvaluation
      ? '📋 Pendiente de Evaluación Médica'
      : '📝 Pendiente de Auto-evaluación',
    color: '#6B7280'
  };
}; 