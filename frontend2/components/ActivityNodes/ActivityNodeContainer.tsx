import React from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
} from "react-native";
import { ActivityNodeViews } from "./index";
import { ResultNodeView } from "./views/ResultNodeView";
import { Ionicons } from "@expo/vector-icons";
import { theme } from "@/src/theme";

interface ActivityNodeContainerProps {
  type: string;
  data: any;
  onNext: ((response?: any) => void) &
    ((response: { answer: string }) => void) &
    ((response: { selectedOption: number }) => void) &
    ((response: { selectedOptions: number[] }) => void) &
    ((response: { value: number }) => void);
  onBack: () => void;
  categoryId?: number;
  responses: { [key: number]: any };
}

export const ActivityNodeContainer: React.FC<ActivityNodeContainerProps> = ({
  type,
  data,
  onNext,
  onBack,
  categoryId,
  responses,
}) => {
  const NodeComponent =
    ActivityNodeViews[type as keyof typeof ActivityNodeViews];

  if (!NodeComponent) {
    console.error(`No view found for node type: ${type}`);
    return null;
  }

  const handleNext = (response?: any) => {
    onNext(response);
  };

  const nodeData = {
    ...data.data,
    id: data.id,
    type: data.type,
  };

  return (
    <View style={styles.container}>
      {onBack && (
        <TouchableOpacity style={styles.backButton} onPress={onBack}>
          <Ionicons name="arrow-back" size={24} color={theme.colors.text} />
          <Text style={styles.backText}>Atrás</Text>
        </TouchableOpacity>
      )}

      <ScrollView
        style={styles.scrollContainer}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={true}
        bounces={false}
      >
        <View style={styles.cardContainer}>
          {type === "RESULT_NODE" ? (
            <ResultNodeView
              data={nodeData}
              onNext={onNext}
              categoryId={categoryId}
              responses={responses}
            />
          ) : (
            <View style={styles.questionContainer}>
              <View style={styles.questionHeader}>
                <Text style={styles.questionType}>
                  {type === "SINGLE_CHOICE_QUESTION" && "Selección Única"}
                  {type === "MULTIPLE_CHOICE_QUESTION" && "Selección Múltiple"}
                  {type === "TEXT_QUESTION" && "Respuesta Abierta"}
                  {type === "SCALE_QUESTION" && "Escala"}
                </Text>
              </View>
              <NodeComponent data={nodeData} onNext={handleNext} />
            </View>
          )}
        </View>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  scrollContainer: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingBottom: 24,
  },
  cardContainer: {
    backgroundColor: theme.colors.card,
    borderRadius: 12,
    padding: 20,
    margin: 16,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
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
  backButton: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 20,
    backgroundColor: theme.colors.card,
    padding: 8,
    borderRadius: 8,
    alignSelf: "flex-start",
  },
  backText: {
    marginLeft: 8,
    fontSize: 16,
    color: theme.colors.text,
    fontWeight: "500",
  },
});
