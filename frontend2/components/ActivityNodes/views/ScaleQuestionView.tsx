import React, { useState } from "react";
import { View, Text, StyleSheet, TouchableOpacity } from "react-native";

import Slider from "@react-native-community/slider";
import { theme } from "@/src/theme";

interface ScaleQuestionProps {
  data: {
    question: string;
    min_value: number;
    max_value: number;
    step: number;
    image?: string;
  };
  onNext?: (response: { value: number }) => void;
}

export function ScaleQuestionView({ data, onNext }: ScaleQuestionProps) {
  const [value, setValue] = useState(data.min_value);

  return (
    <View style={styles.container}>
      <Text style={[styles.question, { color: theme.colors.text }]}>
        {data.question}
      </Text>

      <View style={styles.scaleContainer}>
        <Text style={[styles.valueText, { color: theme.colors.text }]}>
          {value}
        </Text>

        <Slider
          style={styles.slider}
          minimumValue={data.min_value}
          maximumValue={data.max_value}
          step={data.step}
          value={value}
          onValueChange={setValue}
          minimumTrackTintColor={theme.colors.primary}
          maximumTrackTintColor={theme.colors.border}
          thumbTintColor={theme.colors.primary}
        />
      </View>

      <TouchableOpacity
        style={styles.button}
        onPress={() => onNext?.({ value })}
      >
        <Text style={[styles.buttonText, { color: theme.colors.text }]}>
          Continuar
        </Text>
      </TouchableOpacity>
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
  button: {
    backgroundColor: theme.colors.primary,
    padding: 16,
    borderRadius: 8,
    alignItems: "center",
  },
  buttonText: {
    color: "white",
    fontSize: 16,
    fontWeight: "600",
  },
});
