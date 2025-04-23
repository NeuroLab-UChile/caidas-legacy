import { ActivityNodeType } from "@/components/ActivityNodes";

export interface BaseNodeState {
  currentNodeId: number | null;
  history: number[];
}

export interface NodeResponse {
  nodeId: number;
  response: FormattedResponse;
}

export interface FormattedResponse {
  id: number;
  type: ActivityNodeType;
  question: string;
  metadata: {
    timestamp: string;
    version: string;
  };
  answer: any;
}

export interface BaseNode {
  id: number;
  type: ActivityNodeType;
  question?: string;
  options?: any[];
}

export interface NodeHandlers {
  onNext: (response: any) => void;
  onBack: () => void;
  onBefore: () => void;
}

export interface NodeContainerProps {
  type: ActivityNodeType;
  data: BaseNode;
  onNext: (response: any) => void;
  onBack: () => void;
  onBefore: () => void;
  categoryId?: number;
  responses: NodeResponse[];
  currentQuestionIndex: number;
  totalQuestions: number;
  nodeType?: "evaluation" | "training";
}
