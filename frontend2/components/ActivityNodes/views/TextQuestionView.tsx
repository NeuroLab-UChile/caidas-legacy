import React, { useState, useEffect } from "react";
import { View, Text, TextInput, StyleSheet } from "react-native";

import { theme } from "@/src/theme";

interface TextQuestionProps {
  data: {
    question: string;
    image?: string;
    id?: number;
  };
  setResponse: (response: { answer: string } | null) => void;
}

export function TextQuestionView({ data, setResponse }: TextQuestionProps) {
  const [answer, setAnswer] = useState("");

  useEffect(() => {
    setAnswer("");
    setResponse(null);
  }, [data.id, data.question]);

  const handleTextChange = (text: string) => {
    setAnswer(text);
    setResponse(text.trim() ? { answer: text.trim() } : null);
  };

  return (
    <View style={theme.components.activityNode.container}>
      <Text style={theme.components.activityNode.question}>
        {data.question}
      </Text>

      <TextInput
        style={theme.components.activityNode.input}
        value={answer}
        onChangeText={handleTextChange}
        placeholder="Escribe tu respuesta aquí"
        placeholderTextColor={theme.colors.text}
        multiline
        key={data.id || data.question}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  question: {
    fontSize: 18,
    color: theme.colors.text,
    marginBottom: 16,
  },
  input: {
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: 8,
    padding: 12,
    color: theme.colors.text,
    backgroundColor: theme.colors.surface,
  },
  button: {
    marginTop: 16,
    backgroundColor: theme.colors.primary,
    padding: 12,
    borderRadius: 8,
    alignItems: "center",
  },
  buttonText: {
    color: "white",
    fontSize: 16,
    fontWeight: "600",
  },
});
