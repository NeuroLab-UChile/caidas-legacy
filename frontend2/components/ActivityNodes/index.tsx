import { CategoryDescriptionView } from "./views/CategoryDescriptionView";
import { TextQuestionView } from "./views/TextQuestionView";
import { SingleChoiceQuestionView } from "./views/SingleChoiceQuestionView";
import { MultipleChoiceQuestionView } from "./views/MultipleChoiceQuestionView";
import { ScaleQuestionView } from "./views/ScaleQuestionView";
import { ImageQuestionView } from "./views/ImageQuestionView";
import { ResultNodeView } from "./views/ResultNodeView";
import { WeeklyRecipeNodeView } from "./views/WeeklyRecipeNodeView";
import { VideoNodeView } from "./views/VideoNodeView";
import { ImageNodeView } from "./views/ImageNode";
import { TextNodeView } from "./views/TextNodeView";
export const ActivityNodeViews = {
  // Question nodes
  DESCRIPTION_NODE: CategoryDescriptionView,
  SINGLE_CHOICE_QUESTION: SingleChoiceQuestionView,
  MULTIPLE_CHOICE_QUESTION: MultipleChoiceQuestionView,
  TEXT_QUESTION: TextQuestionView,
  SCALE_QUESTION: ScaleQuestionView,
  IMAGE_QUESTION: ImageQuestionView,
  // Training nodes

  VIDEO_NODE: VideoNodeView,
  IMAGE_NODE: ImageNodeView,
  TEXT_NODE: TextNodeView,
  WEEKLY_RECIPE_NODE: WeeklyRecipeNodeView,
  RESULT_NODE: ResultNodeView,
};
export type ActivityNodeType = keyof typeof ActivityNodeViews;
