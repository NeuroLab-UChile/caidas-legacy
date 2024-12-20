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
    data: {
      id: number;
      type: string;
      question: string;
      description?: string;
      options: string[];
    };
  };
  onNext: (response: { selectedOption: number }) => void;
}

export const SingleChoiceQuestionView: React.FC<
  SingleChoiceQuestionViewProps
> = ({ data, onNext }) => {
  const [selected, setSelected] = useState<number | null>(null);
  console.log(data);
  if (!data || !data.data.options) {
    console.error(
      "Missing required data or options in SingleChoiceQuestionView"
    );
    return null;
  }

  return (
    <View style={styles.container}>
      <Text style={styles.question}>{data.data.question}</Text>
      {data.data.options.map((option, index) => (
        <TouchableOpacity
          key={index}
          style={[
            styles.optionButton,
            selected === index && styles.selectedOption,
          ]}
          onPress={() => {
            setSelected(index);
            onNext({ selectedOption: index });
          }}
        >
          <View style={styles.optionContent}>
            <View
              style={[
                styles.radioButton,
                selected === index && styles.radioButtonSelected,
              ]}
            >
              {selected === index && <View style={styles.radioButtonInner} />}
            </View>
            <Text
              style={[
                styles.optionText,
                selected === index && styles.selectedOptionText,
              ]}
            >
              {option}
            </Text>
          </View>
        </TouchableOpacity>
      ))}
    </View>
  );
};

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
  radioButton: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: theme.colors.border,
    alignItems: "center",
    justifyContent: "center",
  },
  radioButtonSelected: {
    borderColor: theme.colors.primary,
  },
  radioButtonInner: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: theme.colors.primary,
  },
  optionText: {
    fontSize: 16,
    color: theme.colors.text,
  },
  selectedOptionText: {
    fontWeight: "600",
  },
});
