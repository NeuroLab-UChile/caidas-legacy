import React from "react";
import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { ActivityNodeViews, ActivityNodeType } from "./index";
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

  return (
    <View style={styles.container}>
      {onBack && (
        <TouchableOpacity style={styles.backButton} onPress={onBack}>
          <Ionicons name="arrow-back" size={24} color={theme.colors.text} />
          <Text style={styles.backText}>Atrás</Text>
        </TouchableOpacity>
      )}

      {type === "RESULT_NODE" ? (
        <ResultNodeView
          data={data}
          onNext={onNext}
          categoryId={categoryId}
          responses={responses}
        />
      ) : (
        <NodeComponent data={data} onNext={handleNext} />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: theme.colors.background,
  },
  backButton: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 16,
  },
  backText: {
    marginLeft: 8,
    fontSize: 16,
    color: theme.colors.text,
  },
});
