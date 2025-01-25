import React, { useState } from "react";
import { View, Text, StyleSheet } from "react-native";
import Slider from "@react-native-community/slider";
import { theme } from "@/src/theme";

interface ScaleQuestionProps {
  data: {
    id: number;
    question: string;
    min_value: number;
    max_value: number;
    step: number;
    image?: string;
  };
  setResponse: (response: { answer: { value: number } } | null) => void;
}

export function ScaleQuestionView({ data, setResponse }: ScaleQuestionProps) {
  const [value, setValue] = useState(data.min_value);

  const handleValueChange = (newValue: number) => {
    setValue(newValue);
    setResponse({
      answer: {
        value: newValue,
      },
    });
  };

  return (
    <View style={theme.components.node.container}>
      <Text style={theme.components.node.question}>{data.question}</Text>

      <View style={styles.scaleContainer}>
        <Text style={styles.valueText}>{value}</Text>

        <Slider
          style={styles.slider}
          minimumValue={data.min_value}
          maximumValue={data.max_value}
          step={data.step}
          value={value}
          onValueChange={handleValueChange}
          minimumTrackTintColor={theme.colors.primary}
          maximumTrackTintColor={theme.colors.border}
          thumbTintColor={theme.colors.primary}
        />

        <View style={styles.labelsContainer}>
          <Text style={styles.labelText}>{data.min_value}</Text>
          <Text style={styles.labelText}>{data.max_value}</Text>
        </View>
      </View>
    </View>
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
    marginBottom: 24,
  },
  scaleContainer: {
    backgroundColor: theme.colors.surface,
    borderRadius: 8,
    padding: 16,
    marginBottom: 24,
  },
  valueText: {
    fontSize: 24,
    color: theme.colors.text,
    textAlign: "center",
    marginBottom: 16,
  },
  slider: {
    width: "100%",
  },
  labelsContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginTop: 8,
  },
  labelText: {
    fontSize: 14,
    color: theme.colors.text,
    opacity: 0.7,
  },
});
