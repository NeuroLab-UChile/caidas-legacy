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
  id: number;
  name: string;
  icon?: string;
  description?: string;
  evaluation_type: string;
  professional_evaluation_result?: string;

  evaluation_form?: {
    question_nodes: QuestionNode[];
  };
  training_form?: {
    training_nodes: TrainingNode[];
  }
  responses?: Record<string, any>;
  completion_date?: string;
  status_color?: {
    color: string;
    text: string;
  };
  professional_recommendations?: string;
  professional_recommendations_updated_by?: {
    name: string;
    date: string;
  };
  professional_recommendations_updated_at?: string;
  is_draft?: boolean;
  recommendations?: string;
  status?: {
    color: string;
    text: string;
  };
}

