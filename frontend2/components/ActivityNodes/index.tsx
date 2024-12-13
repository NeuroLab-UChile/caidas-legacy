import { CategoryDescriptionView } from "./views/CategoryDescriptionView";
import { TextQuestionView } from "./views/TextQuestionView";
import { SingleChoiceQuestionView } from "./views/SingleChoiceQuestionView";
import { MultipleChoiceQuestionView } from "./views/MultipleChoiceQuestionView";
import { ScaleQuestionView } from "./views/ScaleQuestionView";
import { ImageQuestionView } from "./views/ImageQuestionView";
import { ResultNodeView } from "./views/ResultNodeView";

export const ActivityNodeViews = {
  CATEGORY_DESCRIPTION: CategoryDescriptionView,
  TEXT_QUESTION: TextQuestionView,
  SINGLE_CHOICE_QUESTION: SingleChoiceQuestionView,
  MULTIPLE_CHOICE_QUESTION: MultipleChoiceQuestionView,
  SCALE_QUESTION: ScaleQuestionView,
  IMAGE_QUESTION: ImageQuestionView,
  RESULT_NODE: ResultNodeView,
};

export type ActivityNodeType = keyof typeof ActivityNodeViews;
