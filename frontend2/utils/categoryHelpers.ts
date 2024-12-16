export const getCategoryStatus = (category: any) => {
  if (!category?.evaluation_form?.question_nodes) return null;

  const totalQuestions = category.evaluation_form.question_nodes.length;
  const answeredQuestions = Object.keys(category?.responses || {}).length;

  if (category.doctor_recommendations && category.status_color) {
    return {
      status: 'reviewed',
      text: '✅ Evaluación Revisada'
    };
  }

  if (category.completion_date) {
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