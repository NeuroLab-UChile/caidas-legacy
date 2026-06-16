import React from "react";
import {
  View,
  Text,
  Image,
  StyleSheet,
  TouchableOpacity,
  Linking,
} from "react-native";
import { theme } from "@/src/theme";
import { TextWithHyperlinks } from "@/components/ui/TextWithHyperlinks";

interface CategoryDescriptionProps {
  data: {
    title: string;
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
  const description = (
    <TextWithHyperlinks>{data.description}</TextWithHyperlinks>
  );

  return (
    <View style={styles.container}>
      {data.image && (
        <Image
          source={{ uri: data.image }}
          style={styles.image}
          resizeMode="cover"
        />
      )}

      {/* title */}
      <Text
        style={[
          styles.description,
          { color: theme.colors.text, fontWeight: "bold" },
        ]}
      >
        {data.title}
      </Text>

      {/* <Text style={[styles.description, { color: theme.colors.text }]}>
        {data.description}
      </Text> */}
      {description}

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
    marginBottom: theme.typography.sizes.body2,
  },
  description: {
    fontSize: theme.typography.sizes.subtitle,
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
    fontSize: theme.typography.sizes.body1,
    fontWeight: "600",
  },
});
