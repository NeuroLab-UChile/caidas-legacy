import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
} from "react-native";

import { theme } from "@/src/theme";

interface SingleChoiceQuestionViewProps {
  data: {
    id: number;
    type: string;
    question: string;
    description?: string;
    options: string[];
  };
  setResponse: (response: { selectedOption: number }) => void;
}

export function SingleChoiceQuestionView({
  data,
  setResponse,
}: SingleChoiceQuestionViewProps) {
  const [selected, setSelected] = useState<number | null>(null);

  return (
    <View style={theme.components.node.container}>
      <Text style={theme.components.node.question}>{data.question}</Text>

      {data.options.map((option, index) => (
        <TouchableOpacity
          key={index}
          style={[
            theme.components.node.optionButton,
            selected === index && theme.components.node.selectedOption,
          ]}
          onPress={() => {
            setSelected(index);
            setResponse({ selectedOption: index });
          }}
        >
          <View style={theme.components.node.optionContent}>
            <View
              style={[
                theme.components.node.radioButton,
                selected === index && theme.components.node.radioButtonSelected,
              ]}
            >
              {selected === index && (
                <View style={theme.components.node.radioButtonInner} />
              )}
            </View>
            <Text
              style={[
                theme.components.node.optionText,
                selected === index && theme.components.node.selectedOptionText,
              ]}
            >
              {option}
            </Text>
          </View>
        </TouchableOpacity>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    gap: 12,
  },
  question: {
    fontSize: 20,
    fontWeight: "600",
    color: theme.colors.text,
    marginBottom: 24,
    lineHeight: 28,
  },
  optionButton: {
    padding: 16,
    borderRadius: 12,
    backgroundColor: theme.colors.background,
    borderWidth: 2,
    borderColor: theme.colors.border,
  },
  selectedOption: {
    borderColor: theme.colors.primary,
    backgroundColor: `${theme.colors.primary}20`,
  },
  optionContent: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },

  optionText: {
    fontSize: 16,
    color: theme.colors.text,
  },
  selectedOptionText: {
    fontWeight: "600",
  },
});
