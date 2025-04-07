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
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { theme } from "@/src/theme";
import { ActivityNodeViews } from "./index";
import { ResultNodeView } from "./views/ResultNodeView";
import { VideoNodeView } from "./views/VideoNodeView";
import { ImageNodeView } from "./views/ImageNode";
import { router } from 'expo-router';

interface ActivityNodeContainerProps {
  type:
    | "SINGLE_CHOICE_QUESTION"
    | "MULTIPLE_CHOICE_QUESTION"
    | "TEXT_QUESTION"
    | "SCALE_QUESTION"
    | "DESCRIPTION_NODE"
    | "VIDEO_NODE"
    | "IMAGE_NODE"
    | "WEEKLY_RECIPE_NODE"
    | "RESULT_NODE"
    | "IMAGE_QUESTION"
    | "TEXT_NODE";

  data: any;
  onNext: (response?: any) => void;
  onBack: () => void;
  responses: { [key: number]: any };
  categoryId?: number;
  history: number[];
  setHistory: React.Dispatch<React.SetStateAction<number[]>>;
  currentQuestionIndex: number;
  totalQuestions: number;
}

export function ActivityNodeContainer({
  type,
  data,
  onNext,
  onBack,
  responses,
  categoryId,
  history,
  setHistory,
  currentQuestionIndex,
  totalQuestions,
}: ActivityNodeContainerProps) {
  const [currentResponse, setCurrentResponse] = useState<any>(null);

  const NodeComponent =
    ActivityNodeViews[type as keyof typeof ActivityNodeViews];

  const handleNext = () => {
    if (currentResponse && data.question) {
      console.log("currentResponse", currentResponse);
      onNext(currentResponse);
    } else if (!data.question) {
      onNext();
    }
  };

  const handleBack = () => {
    if (history.length > 0) {
      const previousNodeId = history[history.length - 1];
      onBack();
      setHistory(prev => prev.slice(0, -1));
    } else {
      Alert.alert(
        "Salir de la evaluación",
        "¿Estás seguro que deseas salir? Se perderá el progreso.",
        [
          { text: "Cancelar", style: "cancel" },
          {
            text: "Salir",
            style: "destructive",
            onPress: () => {
              router.push("/(tabs)/action");
            }
          }
        ]
      );
    }
  };

  const renderHeader = () => (
    <View>
      <TouchableOpacity style={styles.backButton} onPress={handleBack}>
        <Ionicons name="chevron-back" size={24} color={theme.colors.text} />
        <Text style={styles.backButtonText}>Atrás</Text>
      </TouchableOpacity>
      <Text style={styles.questionCounter}>
        Pregunta {currentQuestionIndex + 1} de {totalQuestions}
      </Text>
    </View>
  );

  const renderContent = () => {
    switch (type) {
      case "RESULT_NODE":
        return (
          <ResultNodeView
            data={data}
            onNext={handleNext}
            responses={responses}
            categoryId={categoryId}
          />
        );
      case "VIDEO_NODE":
        return <VideoNodeView data={data} />;
      case "IMAGE_NODE":
        return <ImageNodeView data={data} />;
      default:
        if (NodeComponent) {
          return (
            <View style={styles.questionContainer}>
              <NodeComponent data={data} setResponse={setCurrentResponse} />
            </View>
          );
        }
        return (
          <View style={styles.contentContainer}>
            <Text style={styles.title}>Nodo desconocido</Text>
            <Text style={styles.description}>
              No se puede renderizar este tipo de nodo.
            </Text>
          </View>
        );
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        style={styles.container}
      >
        <View style={styles.mainContainer}>
          {renderHeader()}
          <ScrollView
            style={styles.scrollView}
            contentContainerStyle={styles.scrollViewContent}
            showsVerticalScrollIndicator={false}
          >
            {renderContent()}
          </ScrollView>
          <TouchableOpacity
            style={[
              styles.nextButton,
              data.question && !currentResponse && styles.nextButtonDisabled,
            ]}
            onPress={handleNext}
            disabled={data.question && !currentResponse}
          >
            <Text
              style={[
                styles.nextText,
                data.question && !currentResponse && styles.nextTextDisabled,
              ]}
            >
              Siguiente
            </Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const BUTTON_HEIGHT = 70;
const BOTTOM_NAV_HEIGHT = 90;

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  container: {
    flex: 1,
  },
  mainContainer: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  disabledButton: {
    backgroundColor: theme.colors.disabled,
  },
  nextButtonDisabled: {
    backgroundColor: theme.colors.disabled,
  },
  nextTextDisabled: {
    color: theme.colors.background,
  },
  backButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    marginBottom: 16,
  },
  backButtonText: {
    marginLeft: 8,
    fontSize: 16,
    color: theme.colors.text,
    fontWeight: '600',
  },
  questionCounter: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginBottom: 16,
  },
  scrollView: {
    flex: 1,
  },
  scrollViewContent: {
    paddingBottom: BUTTON_HEIGHT + 80,
  },
  buttonContainer: {
    position: "absolute",
    bottom: BOTTOM_NAV_HEIGHT, // Posición justo encima del menú
    left: 0,
    right: 0,
    height: BUTTON_HEIGHT,
    backgroundColor: theme.colors.background,
    paddingHorizontal: 16,
    justifyContent: "center",
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
  },
  nextButton: {
    position: "absolute",
    bottom: 24,
    left: 16,
    right: 16,
    alignItems: "center",
    justifyContent: "center",
    padding: 16,
    backgroundColor: theme.colors.primary,
    borderRadius: 12,
    height: BUTTON_HEIGHT - 16,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 4,
    zIndex: 1000,
  },
  nextText: {
    fontSize: 16,
    fontWeight: "600",
    color: theme.colors.text,
  },
  contentContainer: {
    alignItems: "center",
    padding: 16,
  },
  image: {
    width: "100%",
    height: 200,
    borderRadius: 8,
  },
  title: {
    fontSize: 20,
    fontWeight: "600",
    marginTop: 16,
    textAlign: "center",
  },
  description: {
    fontSize: 16,
    textAlign: "center",
    marginTop: 8,
  },
  questionContainer: {
    paddingHorizontal: 20,
    paddingTop: 16,
  },
});

export default ActivityNodeContainer;
