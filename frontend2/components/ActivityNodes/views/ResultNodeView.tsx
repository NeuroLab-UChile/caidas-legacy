import React from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
} from "react-native";

import { theme } from "@/src/theme";

interface ResultNodeProps {
  data: {
    response: {
      title?: string;
      message: string;
      details?: string[];
      type?: "success" | "warning" | "error" | "info";
    };
  };
  onNext?: () => void;
  categoryId?: number;
  responses?: { [key: number]: any };
}

export function ResultNodeView({ data, onNext }: ResultNodeProps) {
  const getResultColor = () => {
    switch (data.response.type) {
      case "success":
        return "#34C759";
      case "warning":
        return "#FF9500";
      case "error":
        return "#FF3B30";
      case "info":
      default:
        return theme.colors.primary;
    }
  };

  return (
    <ScrollView style={theme.components.activityNode.container}>
      <View style={styles.content}>
        {data.response.title && (
          <Text
            style={[
              theme.components.activityNode.question,
              { color: getResultColor() },
            ]}
          >
            {data.response.title}
          </Text>
        )}

        <Text style={theme.components.activityNode.optionText}>
          {data.response.message}
        </Text>

        {data.response.details && data.response.details.length > 0 && (
          <View style={styles.detailsContainer}>
            {data.response.details.map((detail, index) => (
              <Text
                key={`detail-${data.response.type}-${index}`}
                style={theme.components.activityNode.optionText}
              >
                • {detail}
              </Text>
            ))}
          </View>
        )}

        <TouchableOpacity
          style={[
            theme.components.activityNode.button,
            { backgroundColor: getResultColor() },
          ]}
          onPress={onNext}
        >
          <Text style={theme.components.activityNode.buttonText}>
            Continuar
          </Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  content: {
    padding: 16,
    flex: 1,
  },
  detailsContainer: {
    marginBottom: 24,
    paddingHorizontal: 8,
  },
});
