import { useState, useEffect, useCallback, memo } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Platform,
  AccessibilityInfo,
  AccessibilityRole,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { theme } from "@/src/theme";

interface Option {
  id: number;
  text: string;
}

interface MultipleChoiceQuestionProps {
  data: {
    id: number;
    type: string;
    question: string;
    description?: string;
    options: string[];
  };
  setResponse: (response: { selectedOptions: number[] } | null) => void;
  onNext?: () => void;
  maxSelections?: number;
}

const OptionButton = memo(
  ({
    option,
    isSelected,
    onToggle,
  }: {
    option: Option;
    isSelected: boolean;
    onToggle: (id: number) => void;
  }) => (
    <TouchableOpacity
      key={`option-${option.id}`}
      style={[styles.optionButton, isSelected && styles.selectedOptionButton]}
      onPress={() => onToggle(option.id)}
      activeOpacity={0.7}
      accessibilityRole="checkbox"
      accessibilityState={{ checked: isSelected }}
      accessibilityLabel={`${option.text}, ${isSelected ? "seleccionado" : "no seleccionado"}`}
      accessibilityHint="Toca para seleccionar o deseleccionar esta opción"
    >
      <View style={styles.optionContent}>
        <Ionicons
          name={isSelected ? "checkbox" : "square-outline"}
          size={24}
          color={isSelected ? theme.colors.primary : theme.colors.text}
          style={styles.checkbox}
        />
        <Text
          style={[styles.optionText, isSelected && styles.selectedOptionText]}
          numberOfLines={3}
        >
          {option.text}
        </Text>
      </View>
    </TouchableOpacity>
  ),
);

OptionButton.displayName = "OptionButton";

export function MultipleChoiceQuestionView({
  data,
  setResponse,
  maxSelections = Infinity,
}: MultipleChoiceQuestionProps) {
  const [selectedOptions, setSelectedOptions] = useState<number[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setSelectedOptions([]);
    setResponse(null);
    setError(null);
  }, [data.question]);

  const toggleOption = useCallback(
    (optionId: number) => {
      setSelectedOptions((prev) => {
        const isCurrentlySelected = prev.includes(optionId);
        let newSelection: number[];

        if (isCurrentlySelected) {
          newSelection = prev.filter((id) => id !== optionId);
        } else {
          if (prev.length >= maxSelections) {
            setError(`Puedes seleccionar máximo ${maxSelections} opciones`);
            return prev;
          }
          newSelection = [...prev, optionId];
          setError(null);
        }

        setResponse(
          newSelection.length > 0 ? { selectedOptions: newSelection } : null,
        );
        return newSelection;
      });
    },
    [maxSelections, setResponse],
  );

  const formattedOptions: Option[] = data.options.map(
    (option: string, index: number) => ({
      id: index,
      text: option,
    }),
  );

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.contentContainer}
      showsVerticalScrollIndicator={true}
      bounces={true}
      alwaysBounceVertical={true}
      accessibilityRole="radiogroup"
      accessibilityLabel="Lista de opciones múltiples"
    >
      <View accessible={true}>
        <Text style={styles.questionText} accessibilityRole="header">
          {data.question}
        </Text>
        {data.description && (
          <Text style={styles.description}>{data.description}</Text>
        )}
      </View>

      <View style={styles.optionsContainer}>
        {formattedOptions.map((option) => (
          <OptionButton
            key={option.id}
            option={option}
            isSelected={selectedOptions.includes(option.id)}
            onToggle={toggleOption}
          />
        ))}
      </View>

      {error && (
        <Text style={styles.errorText} accessibilityRole="alert">
          {error}
        </Text>
      )}

      {selectedOptions.length > 0 && (
        <Text
          style={styles.selectionCount}
          accessibilityRole="text"
          accessibilityLabel={`${selectedOptions.length} ${
            selectedOptions.length === 1
              ? "opción seleccionada"
              : "opciones seleccionadas"
          }`}
        >
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
    marginBottom: 16,
    lineHeight: 28,
  },
  description: {
    fontSize: 16,
    color: theme.colors.text,
    opacity: 0.8,
    marginBottom: 24,
    lineHeight: 22,
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
  errorText: {
    fontSize: 14,
    color: theme.colors.error || "#dc2626",
    textAlign: "center",
    marginTop: 8,
    marginBottom: 8,
  },
});
