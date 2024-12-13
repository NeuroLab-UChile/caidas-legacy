import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
} from "react-native";

import { theme } from "@/src/theme";
interface SingleChoiceQuestionProps {
  data: {
    id: number;
    question: string;
    options: string[];
    image?: string;
  };
  onNext?: (response: { selectedOption: number }) => void;
}

export function SingleChoiceQuestionView({
  data,
  onNext,
}: SingleChoiceQuestionProps) {
  const [selectedOption, setSelectedOption] = useState<number | null>(null);

  return (
    <ScrollView style={theme.components.activityNode.container}>
      <Text style={theme.components.activityNode.question}>
        {data.question}
      </Text>

      <View style={styles.optionsContainer}>
        {data.options.map((option, index) => (
          <TouchableOpacity
            key={`question-${data.id}-option-${index}`}
            style={[
              theme.components.activityNode.option,
              selectedOption === index &&
                theme.components.activityNode.selectedOption,
            ]}
            onPress={() => setSelectedOption(index)}
          >
            <Text style={theme.components.activityNode.optionText}>
              {option}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <TouchableOpacity
        style={theme.components.activityNode.button}
        onPress={() => selectedOption !== null && onNext?.({ selectedOption })}
        disabled={selectedOption === null}
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
    marginBottom: 24,
    paddingHorizontal: 16,
  },
  option: {
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
  },
  optionText: {
    fontSize: 16,
  },
  button: {
    margin: 16,
    padding: 16,
    borderRadius: 8,
    alignItems: "center",
  },
  buttonText: {
    color: "white",
    fontSize: 16,
    fontWeight: "500",
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
  },
  selectedOption: {
    backgroundColor: theme.colors.primary + "20",
    borderColor: theme.colors.primary,
  },
});
