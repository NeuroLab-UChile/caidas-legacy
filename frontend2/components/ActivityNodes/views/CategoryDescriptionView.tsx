import React from "react";
import { View, Text, Image, StyleSheet, TouchableOpacity } from "react-native";

import { theme } from "@/src/theme";

interface CategoryDescriptionProps {
  data: {
    description: string;
    image?: string;
    first_button_text?: string;
    second_button_text?: string;
  };
  onNext?: (response?: any) => void;
}

export function CategoryDescriptionView({
  data,
  onNext,
}: CategoryDescriptionProps) {
  return (
    <View style={styles.container}>
      {data.image && (
        <Image
          source={{ uri: data.image }}
          style={styles.image}
          resizeMode="cover"
        />
      )}

      <Text style={[styles.description, { color: theme.colors.text }]}>
        {data.description}
      </Text>

      <View style={styles.buttonContainer}>
        {data.first_button_text && (
          <TouchableOpacity
            style={[styles.button, { backgroundColor: theme.colors.primary }]}
            onPress={() => onNext?.({ button: 1 })}
          >
            <Text style={styles.buttonText}>{data.first_button_text}</Text>
          </TouchableOpacity>
        )}

        {data.second_button_text && (
          <TouchableOpacity
            style={[styles.button, { backgroundColor: theme.colors.primary }]}
            onPress={() => onNext?.({ button: 2 })}
          >
            <Text style={styles.buttonText}>{data.second_button_text}</Text>
          </TouchableOpacity>
        )}
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
  image: {
    width: "100%",
    height: 200,
    borderRadius: 8,
    marginBottom: 16,
  },
  description: {
    fontSize: 18,
    color: theme.colors.text,
    marginBottom: 24,
    textAlign: "center",
  },
  buttonContainer: {
    width: "100%",
    gap: 12,
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
