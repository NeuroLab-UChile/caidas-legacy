import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  SafeAreaView,
  Platform,
  Image,
  KeyboardAvoidingView,
  Alert,
  Modal,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { theme } from "@/src/theme";
import { ActivityNodeViews, ActivityNodeType } from "./index";
import { ResultNodeView } from "./views/ResultNodeView";
import { VideoNodeView } from "./views/VideoNodeView";
import { ImageNodeView } from "./views/ImageNode";
import { router } from "expo-router";
import { StepIndicator } from "../ui/StepIndicator";
import { NavigationBar } from "../ui/NavigationBar";
import { TextNodeView } from "./views/TextNodeView";
import { SingleChoiceQuestionView } from "./views/SingleChoiceQuestionView";
import { MultipleChoiceQuestionView } from "./views/MultipleChoiceQuestionView";
import { TextQuestionView } from "./views/TextQuestionView";
import { ScaleQuestionView } from "./views/ScaleQuestionView";
import { ImageQuestionView } from "./views/ImageQuestionView";
import { WeeklyRecipeNodeView } from "./views/WeeklyRecipeNodeView";
import { CategoryDescriptionView } from "./views/CategoryDescriptionView";
import { commonStyles } from "./styles/commonStyles";
import { apiService } from "@/app/services/apiService";

interface ActivityNodeContainerProps {
  type: ActivityNodeType;
  data: any;
  onNext?: (response?: any) => void;
  onBefore?: () => void;
  onBack?: () => void;
  categoryId?: number;
  responses?: any[];
  currentQuestionIndex: number;
  totalQuestions: number;
  nodeType?: "training" | "evaluation";
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
    marginBottom: 40,
  },
  content: {
    flex: 1,
    padding: 16,
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  header: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  footer: {
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
    backgroundColor: theme.colors.background,
  },
  btn: {
    flex: 1,
    height: 56,
    borderRadius: 16,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: theme.colors.primary,
    borderWidth: 1,
    borderColor: "#000",
    fontWeight: "600",
    color: "#000",
  },
  btnOutline: {
    backgroundColor: "transparent",
    borderWidth: 1,
    borderColor: theme.colors.primary,
  },
  btnDisabled: {
    backgroundColor: theme.colors.disabled,
    borderColor: "transparent",
  },
  text: {
    fontSize: 17,
    color: "#000",
    fontWeight: "600",
  },
});

export const ActivityNodeContainer: React.FC<ActivityNodeContainerProps> = ({
  type,
  data,
  onNext,
  onBefore,
  onBack,
  categoryId,
  responses = [],
  currentQuestionIndex,
  totalQuestions,
  nodeType = "training",
}) => {
  const [currentResponse, setCurrentResponse] = useState<any>(null);

  const handleNext = (response?: any) => {
    console.log("Handling next step with response:", currentResponse);
    apiService.activityLog.trackAction(
      `node_next ${categoryId} ${currentQuestionIndex + 1}/${totalQuestions}`
    );

    // Mostrar Toast de que la imagen se guardo correctamente
    if (type === "IMAGE_QUESTION") {
      const nimages = currentResponse?.answer.length;
      if (nimages == 1) {
        Alert.alert("", "Imagen guardada correctamente");
      } else if (nimages > 1) {
        Alert.alert("", "Imágenes guardadas correctamente");
      } else {
        Alert.alert("", "No se seleccionaron imágenes");
      }
    }

    if (onNext) {
      // onNext(response || currentResponse); // [JV] This seems to be the critical bug
      onNext(currentResponse);
      // Clean currentResponse
      setCurrentResponse(null);
    }
  };

  const renderContent = () => {
    const commonProps = {
      data,
      onNext: handleNext,
      setResponse: setCurrentResponse,
    };

    switch (type) {
      case "VIDEO_NODE":
        return <VideoNodeView {...commonProps} />;
      case "RESULT_NODE":
        return <ResultNodeView {...commonProps} />;
      case "WEEKLY_RECIPE_NODE":
        return <WeeklyRecipeNodeView data={data} />;
      case "IMAGE_NODE":
        return <ImageNodeView {...commonProps} />;
      case "TEXT_NODE":
        return <TextNodeView data={data} />;
      case "DESCRIPTION_NODE":
        return <CategoryDescriptionView {...commonProps} />;
      case "SINGLE_CHOICE_QUESTION":
        return <SingleChoiceQuestionView {...commonProps} />;
      case "MULTIPLE_CHOICE_QUESTION":
        return <MultipleChoiceQuestionView {...commonProps} />;
      case "TEXT_QUESTION":
        return <TextQuestionView {...commonProps} />;
      case "SCALE_QUESTION":
        return <ScaleQuestionView {...commonProps} />;
      case "IMAGE_QUESTION":
        return <ImageQuestionView {...commonProps} />;
      default:
        return null;
    }
  };

  const getButtonText = () => {
    console.log("Current type:", type);
    // console.log("Current response:", currentResponse);
    switch (type) {
      case "RESULT_NODE":
        return "Finalizar";
      case "WEEKLY_RECIPE_NODE":
        return "Continuar";
      default:
        return "Siguiente";
    }
  };

  return (
    <View style={styles.container}>
      <View style={[styles.row, styles.header]}>
        <TouchableOpacity onPress={onBack}>
          <Text style={styles.text}>Salir</Text>
        </TouchableOpacity>
        <StepIndicator
          current={currentQuestionIndex + 1}
          total={totalQuestions}
        />
        <View style={{ width: 40 }} />
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {renderContent()}
      </ScrollView>

      <View style={styles.footer}>
        <View style={styles.row}>
          {currentQuestionIndex > 0 && (
            <TouchableOpacity
              style={[styles.btn, styles.btnOutline]}
              onPress={onBefore}
            >
              <Text style={styles.text}>Anterior</Text>
            </TouchableOpacity>
          )}
          <TouchableOpacity
            style={[
              styles.btn,
              type.includes("QUESTION") &&
                !currentResponse &&
                styles.btnDisabled,
            ]}
            onPress={handleNext}
            disabled={type.includes("QUESTION") && !currentResponse}
          >
            <Text style={styles.text}>{getButtonText()}</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
};

export default ActivityNodeContainer;
