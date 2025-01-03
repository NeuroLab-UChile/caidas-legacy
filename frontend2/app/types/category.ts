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
  completed_date: string | null;
  is_completed: boolean;
  responses: Record<string, any>; // Respuestas de los nodos
  question_nodes: QuestionNode[];
  professional_responses?: Record<string, any>;
  updated_at?: string;
}

/**
 * Representa el estado de una categoría.
 */
export interface Status {
  color: string; // Código de color (e.g., "#808080").
  text: string; // Texto descriptivo del estado.
  is_completed: boolean; // Indica si se completó.
  is_draft: boolean; // Indica si está en borrador.
  last_updated: string | null; // Última fecha de actualización.
  professional_reviewed: boolean | null; // Si fue revisado por un profesional.
}

/**
 * Representa las recomendaciones asociadas a una categoría.
 */
export interface Recommendation {
  status: Status; // Estado de la recomendación.
  text: string | null; // Texto de la recomendación.
  updated_at: string | null; // Fecha de la última actualización.
  is_draft: boolean; // Indica si está en borrador.
  professional?: {
    name: string; // Nombre del profesional que actualizó.
  };
}

/**
 * Representa el formulario de evaluación.
 */

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
  // Identificación básica
  id: number; // ID único.
  name: string; // Nombre de la categoría.
  icon: string | null; // URL del ícono.
  description: string | null; // Descripción de la categoría.

  // Evaluación
  evaluation_type: "SELF" | "PROFESSIONAL" | "BOTH"; // Tipo de evaluación.
  evaluation_form: EvaluationForm; // Formulario de evaluación.


  // Estado y recomendaciones
  status: Status; // Estado actual.
  recommendations: Recommendation | null; // Recomendaciones asociadas.

  // Entrenamiento
  training_form: TrainingForm | null; // Formulario de entrenamiento.
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
