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
  type: 'TEXT_NODE' | 'VIDEO_NODE' | 'IMAGE_NODE' | 'WEEKLY_RECIPE_NODE';
  title: string;
  description: string;
  media_url?: string;
  next_node_id: number | null;
}

export interface Category {
  id: number;
  name: string;
  icon?: string;
  description?: string;

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

