import { Category } from "../app/types/category";

export const getCategoryStatus = (category: Category) => {
  const { icon, ...categoryWithoutIcon } = category;
  console.log('Category:', categoryWithoutIcon);

  if (!category?.evaluation_form?.question_nodes) return null;

  const totalQuestions = category.evaluation_form.question_nodes.length;
  const answeredQuestions = Object.keys(category?.responses || {}).length;

  if (category.professional_evaluation_results && category.status_color) {
    return {
      status: 'reviewed',
      text: '✅ Evaluación Revisada por Doctor'
    };
  }

  if (answeredQuestions === totalQuestions && category.evaluation_form.completion_date) {
    return {
      status: 'completed',
      text: '✅ Evaluación Completada'
    };
  }

  if (answeredQuestions > 0) {
    return {
      status: 'in_progress',
      text: `📝 Evaluación en Progreso (${answeredQuestions}/${totalQuestions})`
    };
  }

  return {
    status: 'pending',
    text: '📝 Evaluación Pendiente'
  };
}; 