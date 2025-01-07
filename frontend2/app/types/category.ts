import { ActivityNodeType } from "@/components/ActivityNodes";

/**
 * Tipo para los nodos de preguntas en evaluaciones.
 */
export interface QuestionNode {
  id: number;
  type: ActivityNodeType;
  question: string;
  options?: string[];
  image?: string;
  next_node_id: number | null;
  required?: boolean;
  order?: number;
}

/**
 * Representa los resultados de una evaluación.
 */
export interface EvaluationForm {
  completed_date: string;
  professional_responses?: ProfessionalResponses;
  question_nodes: QuestionNode[];
  responses: Record<string, any>;
  updated_at: string;
}

/**
 * Representa el estado de una categoría o recomendación.
 */
export interface Status {
  color: string;
  text: string;
  is_completed?: boolean;
  is_draft?: boolean;
  last_updated?: string;
  professional_reviewed?: boolean;
}

/**
 * Representa las recomendaciones profesionales.
 */
export interface Recommendation {
  is_draft: boolean;
  professional: {
    name: string;
    role: string;
  };
  status: {
    color: string;
    text: string;
  };
  text: string;
  updated_at: string;
}

/**
 * Representa las respuestas profesionales.
 */
export interface ProfessionalResponses {
  diagnosis: string;
  observations: string;
}

/**
 * Representa el formulario de entrenamiento.
 */
export interface TrainingForm {
  training_nodes: TrainingNode[];
}

/**
 * Representa un nodo de entrenamiento.
 */
export interface TrainingNode {
  id: number;
  type: string;
  content: string;
  options?: any[];
}

/**
 * Representa una categoría de evaluación.
 */
export interface Category {
  description: string;
  evaluation_form: EvaluationForm;
  evaluation_type: {
    label: string;
    type: 'PROFESSIONAL' | 'SELF';
  };
  id: number;
  name: string;
  recommendations: Recommendation;
  status: {
    color: string;
    is_completed: boolean;
    is_draft: boolean;
    last_updated: string;
    professional_reviewed: boolean;
    text: string;
  };
  training_form?: {
    training_nodes: TrainingNode[];
  };
  icon?: string;
}

/**
 * Representa un nodo raíz en el sistema.
 */
export interface RootNode {
  type: ActivityNodeType;
  description: string;
  first_button_text: string;
  first_button_node_id: number;
}
