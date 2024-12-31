import { ActivityNodeType } from "@/components/ActivityNodes";

export interface QuestionNode {
  id: number;
  type: ActivityNodeType;

  question: string;
  options?: string[];
  image?: string;

  next_node_id: number | null;
}

export interface EvaluationForm {
  id: number;
  question_nodes: QuestionNode[];
  completion_date?: string;
  score?: number;
  recommendations?: string[];
}

export interface RootNode {
  type: ActivityNodeType;
  description: string;
  first_button_text: string;
  first_button_node_id: number;
}

export interface TrainingNode {
  id: number;
  type: string;
  content: string;
  options?: any[];
  // Add any other properties your nodes might have
}

export interface NodeResponse {
  nodeId: number;
  response: any;
}

export interface TrainingState {
  currentNodeId: number | null;
  history: number[];
  trainingResult: {
    initial_node_id: number | null;
    nodes: TrainingNode[];
  };
}

export interface Category {
  // Basic Information
  id: number;
  name: string | null;
  icon: string | null;
  description: string | null;

  // Evaluation Configuration
  evaluation_type:
  'SELF' | 'PROFESSIONAL' | 'BOTH';


  evaluation_form: {
    question_nodes: QuestionNode[];
  } | null;

  evaluation_results: {
    data: any;
    date: string;
    updated_at: string;
    professional?: {
      id: number;
      name: string;
    };
  } | null;

  training_form: {
    training_nodes: TrainingNode[];
  } | null;

  // Status and Completion
  status: {
    color: {
      color: string;
      text: string;
    };
    draft: 'Borrador' | 'Publicado';
    has_evaluation: boolean;
    professional_reviewed: boolean;
  };

  // Professional Evaluation
  professional_evaluation_results: string | null;

  // Recommendations
  recommendations: {
    status: {
      color: string;
      text: string;
    };
    professional: {
      id: number;
      name: string;
    } | null;
    updated_at: string | null;
    text: string | null;
  } | null;

  // Other fields
  completion_date: string | null;
  responses: Record<string, any> | null;
  status_color: 'verde' | 'amarillo' | 'rojo' | 'gris' | null;
  is_draft: boolean;
}

