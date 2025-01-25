import React from "react";
import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { theme } from "@/src/theme";
import { router } from "expo-router";

export default function EmptyState({
  view,
}: {
  view: "training" | "evaluate";
}) {
  return (
    <View style={styles.container}>
      {/* Header */}

      {/* Content */}
      <View style={styles.content}>
        <Text style={styles.title}>Sin categoría seleccionada</Text>
        <Text style={styles.subtitle}>
          {view === "training"
            ? "Para comenzar tu entrenamiento, selecciona una categoría."
            : "Para comenzar tu evaluación, selecciona una categoría."}
        </Text>
        <TouchableOpacity
          style={styles.button}
          onPress={() => router.push("/action")}
        >
          <Text style={styles.buttonText}>Seleccionar Categoría</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
    justifyContent: "space-between",
  },
  header: {
    backgroundColor: theme.colors.primary,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  headerText: {
    color: theme.colors.text,
    fontSize: 20,
    fontWeight: "bold",
  },
  exitButton: {
    color: theme.colors.text,
    fontSize: 16,
  },
  content: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 24,
  },
  title: {
    fontSize: 22,
    fontWeight: "600",
    color: theme.colors.text,
    marginBottom: 12,
    textAlign: "center",
  },
  subtitle: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    textAlign: "center",
    marginBottom: 24,
  },
  button: {
    backgroundColor: theme.colors.primary,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: "center",
  },
  buttonText: {
    fontSize: 16,
    color: theme.colors.text,
    fontWeight: "bold",
  },
});
