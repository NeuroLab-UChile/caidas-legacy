import  { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Platform,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { theme } from "@/src/theme";

interface MultipleChoiceQuestionProps {
  data: {
    question: string;
    options: Array<string>;
    image?: string;
  };
  setResponse: (response: { selectedOptions: number[] } | null) => void;
}

export function MultipleChoiceQuestionView({
  data,
  setResponse,
}: MultipleChoiceQuestionProps) {
  const [selectedOptions, setSelectedOptions] = useState<number[]>([]);

  useEffect(() => {
    setSelectedOptions([]);
    setResponse(null);
  }, [data.question]);

  const toggleOption = (optionId: number) => {
    const newSelection = selectedOptions.includes(optionId)
      ? selectedOptions.filter((id) => id !== optionId)
      : [...selectedOptions, optionId];

    setSelectedOptions(newSelection);
    setResponse(
      newSelection.length > 0 ? { selectedOptions: newSelection } : null
    );
  };

  const formattedOptions = data.options.map(
    (option: string, index: number) => ({
      id: index,
      text: option,
    })
  );

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.contentContainer}
      showsVerticalScrollIndicator={true}
      bounces={true}
      alwaysBounceVertical={true}
    >
      <View>
        <Text style={styles.questionText}>{data.question}</Text>
      </View>

      <View style={styles.optionsContainer}>
        {formattedOptions.map((option, index) => {
          const isSelected = selectedOptions.includes(option.id);
          return (
            <TouchableOpacity
              key={`option-${index}`}
              style={[
                styles.optionButton,
                isSelected && styles.selectedOptionButton,
              ]}
              onPress={() => toggleOption(option.id)}
              activeOpacity={0.7}
            >
              <View style={styles.optionContent}>
                <Ionicons
                  name={isSelected ? "checkbox" : "square-outline"}
                  size={24}
                  color={isSelected ? theme.colors.primary : theme.colors.text}
                  style={styles.checkbox}
                />
                <Text
                  style={[
                    styles.optionText,
                    isSelected && styles.selectedOptionText,
                  ]}
                >
                  {option.text}
                </Text>
              </View>
            </TouchableOpacity>
          );
        })}
      </View>

      {selectedOptions.length > 0 && (
        <Text style={styles.selectionCount}>
          {selectedOptions.length}{" "}
          {selectedOptions.length === 1
            ? "opción seleccionada"
            : "opciones seleccionadas"}
        </Text>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  contentContainer: {
    padding: 20,
    paddingBottom: 40,
    flexGrow: 1,
    minHeight: "100%",
  },
  questionText: {
    fontSize: 20,
    fontWeight: "600",
    color: theme.colors.text,
    marginBottom: 24,
    lineHeight: 28,
  },
  optionsContainer: {
    gap: 12,
    marginBottom: 32,
  },
  optionButton: {
    backgroundColor: "#FFFFFF",
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: theme.colors.border,
    marginBottom: 8,
    ...Platform.select({
      ios: {
        shadowColor: "#000",
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
      },
      android: {
        elevation: 2,
      },
    }),
  },
  optionContent: {
    flexDirection: "row",
    alignItems: "center",
  },
  selectedOptionButton: {
    backgroundColor: `${theme.colors.primary}15`,
    borderColor: theme.colors.primary,
  },
  checkbox: {
    marginRight: 12,
  },
  optionText: {
    fontSize: 16,
    color: "#000000",
    flex: 1,
    lineHeight: 24,
  },
  selectedOptionText: {
    color: theme.colors.text,
    fontWeight: "500",
  },
  selectionCount: {
    fontSize: 14,
    color: theme.colors.text,
    opacity: 0.7,
    textAlign: "center",
    marginTop: 16,
  },
});
