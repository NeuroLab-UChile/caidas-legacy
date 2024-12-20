import React from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Image,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { theme } from "@/src/theme";
import { ActivityNodeViews } from "./index";
import { ResultNodeView } from "./views/ResultNodeView";
import { VideoNodeView } from "./views/VideoNodeView";

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
    | "IMAGE_QUESTION";
  data: any;
  onNext: ((response?: any) => void) &
    ((response: { answer: string }) => void) &
    ((response: { selectedOption: number }) => void) &
    ((response: { selectedOptions: number[] }) => void) &
    ((response: { value: number }) => void);
  onBack: () => void;
  responses: { [key: number]: any };
  categoryId?: number;
}

const ActivityNodeContainer: React.FC<ActivityNodeContainerProps> = ({
  type,
  data,
  onNext,
  onBack,
  responses,
  categoryId,
}) => {
  const NodeComponent =
    ActivityNodeViews[type as keyof typeof ActivityNodeViews];

  console.log(data);

  const handleNext = (response?: any) => {
    onNext(response);
  };

  const renderHeader = () => (
    <TouchableOpacity style={styles.backButton} onPress={onBack}>
      <Ionicons name="arrow-back" size={24} color={theme.colors.text} />
      <Text style={styles.backText}>Atrás</Text>
    </TouchableOpacity>
  );

  const renderContent = () => {
    switch (type) {
      default:
        if (NodeComponent) {
          return (
            <View style={styles.questionContainer}>
              <View style={styles.questionHeader}>
                <Text style={styles.questionType}>
                  {type === "SINGLE_CHOICE_QUESTION" && "Selección Únic"}
                  {type === "MULTIPLE_CHOICE_QUESTION" && "Selección Múltiple"}
                  {type === "TEXT_QUESTION" && "Respuesta Abierta"}
                  {type === "SCALE_QUESTION" && "Escala"}
                </Text>
              </View>
              <NodeComponent data={data} onNext={handleNext} />
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
    <ScrollView style={styles.container}>
      {renderHeader()}
      <View style={styles.card}>{renderContent()}</View>
      <TouchableOpacity style={styles.nextButton} onPress={() => onNext()}>
        <Text style={styles.nextText}>Siguiente</Text>
      </TouchableOpacity>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  backButton: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 16,
    padding: 10,
  },
  backText: {
    marginLeft: 8,
    fontSize: 16,
    color: theme.colors.text,
  },
  card: {
    backgroundColor: theme.colors.card,
    borderRadius: 12,
    padding: 16,
    margin: 16,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  contentContainer: {
    alignItems: "center",
  },
  title: {
    fontSize: 20,
    fontWeight: "600",
    marginBottom: 12,
    textAlign: "center",
    color: theme.colors.text,
  },
  description: {
    fontSize: 16,
    textAlign: "center",
    color: theme.colors.textSecondary,
  },
  image: {
    width: "100%",
    height: 200,
    marginBottom: 16,
    borderRadius: 8,
  },
  questionContainer: {
    gap: 16,
  },
  questionHeader: {
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
    paddingBottom: 12,
    marginBottom: 16,
  },
  questionType: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    fontWeight: "600",
    textTransform: "uppercase",
  },
  nextButton: {
    alignItems: "center",
    padding: 16,
    margin: 16,
    backgroundColor: theme.colors.primary,
    borderRadius: 8,
  },
  nextText: {
    fontSize: 16,
    fontWeight: "600",
    color: theme.colors.text,
  },
});

export default ActivityNodeContainer;
