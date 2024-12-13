import { ActivityNodeType } from "@/components/ActivityNodes";

export interface QuestionNode {
  id: number;
  type: ActivityNodeType;
  data: {
    question: string;
    options?: string[];
    image?: string;
  };
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

export interface Category {
  id: number;
  name: string;
  icon: string;
  description: string;
  root_node: RootNode;
  evaluation_form: EvaluationForm;
  responses?: { [key: number]: any };
} 