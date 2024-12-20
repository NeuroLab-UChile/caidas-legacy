import { ActivityNodeContainer } from "@/components/ActivityNodes/ActivityNodeContainer";
import { QuestionNode, TrainingNode } from "@/app/types/category";

interface RenderNodeProps {
  node: QuestionNode | TrainingNode | null;
  onNext: (response: any) => void;
  onBack: () => void;
  categoryId?: number;
  responses: { [key: number]: any };
}

export const renderActivityNode = ({
  node,
  onNext,
  onBack,
  categoryId,
  responses,
}: RenderNodeProps) => {
  console.log("node", node);

  if (!node) return null;

  return (
    <ActivityNodeContainer
      type={node.type}
      data={node}
      onNext={(response) => onNext(response)}
      onBack={onBack}
      categoryId={categoryId}
      responses={responses}
    />
  );
};
