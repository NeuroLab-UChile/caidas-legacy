import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
} from "react-native";

import { Ionicons } from "@expo/vector-icons";
import { theme } from "@/src/theme";

interface MultipleChoiceQuestionProps {
  data: {
    question: string;
    options: Array<{
      id: number;
      text: string;
    }>;
    image?: string;
  };
  onNext?: (response: { selectedOptions: number[] }) => void;
}

export function MultipleChoiceQuestionView({
  data,
  onNext,
}: MultipleChoiceQuestionProps) {
  const [selectedOptions, setSelectedOptions] = useState<number[]>([]);

  const toggleOption = (optionId: number) => {
    setSelectedOptions((prev) =>
      prev.includes(optionId)
        ? prev.filter((id) => id !== optionId)
        : [...prev, optionId]
    );
  };

  return (
    <ScrollView style={theme.components.activityNode.container}>
      <Text style={theme.components.activityNode.question}>
        {data.question}
      </Text>

      <View style={styles.optionsContainer}>
        {data.options.map((option) => (
          <TouchableOpacity
            key={`multiple-choice-${option.id}`}
            style={[
              theme.components.activityNode.option,
              selectedOptions.includes(option.id) &&
                theme.components.activityNode.selectedOption,
            ]}
            onPress={() => toggleOption(option.id)}
          >
            <Ionicons
              name={
                selectedOptions.includes(option.id)
                  ? "checkbox"
                  : "square-outline"
              }
              size={24}
              color={theme.colors.text}
              style={styles.checkbox}
            />
            <Text style={theme.components.activityNode.optionText}>
              {option.text}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <TouchableOpacity
        style={theme.components.activityNode.button}
        onPress={() =>
          selectedOptions.length > 0 && onNext?.({ selectedOptions })
        }
        disabled={selectedOptions.length === 0}
      >
        <Text style={theme.components.activityNode.buttonText}>Continuar</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
    padding: 16,
  },
  question: {
    fontSize: 18,
    color: theme.colors.text,
    marginBottom: 16,
  },
  optionsContainer: {
    gap: 12,
    marginVertical: 24,
  },
  option: {
    flexDirection: "row",
    alignItems: "center",
  },
  checkbox: {
    marginRight: 12,
  },
  optionContainer: {
    backgroundColor: theme.colors.surface,
    borderRadius: 8,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  optionButton: {
    padding: 16,
    flexDirection: "row",
    alignItems: "center",
  },
  optionText: {
    fontSize: 16,
    color: theme.colors.text,
    marginLeft: 12,
  },
  selectedOption: {
    backgroundColor: theme.colors.primary + "20",
    borderColor: theme.colors.primary,
  },
  submitButton: {
    marginTop: 16,
    backgroundColor: theme.colors.primary,
    padding: 16,
    borderRadius: 8,
    alignItems: "center",
  },
  submitButtonText: {
    color: "white",
    fontSize: 16,
    fontWeight: "600",
  },
  button: {
    backgroundColor: theme.colors.primary,
    padding: 16,
    borderRadius: 8,
    alignItems: "center",
  },
  buttonText: {
    fontSize: 16,
    fontWeight: "600",
  },
});
