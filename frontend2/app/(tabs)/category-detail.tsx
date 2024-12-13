import React from "react";
import { View, Text, StyleSheet, ScrollView } from "react-native";
import { useCategories } from "../contexts/categories";
import { useCustomTheme } from "@/src/hooks/useCustomTheme";

export default function CategoryDetailScreen() {
  const { selectedCategory } = useCategories();
  const theme = useCustomTheme();

  if (!selectedCategory) {
    return (
      <View style={styles.container}>
        <Text style={[styles.errorText, { color: theme.colors.text }]}>
          No hay categoría seleccionada
        </Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: theme.colors.background }]}
      contentContainerStyle={styles.contentContainer}
    >
      <Text style={[styles.title, { color: theme.colors.text }]}>
        {selectedCategory.name}
      </Text>

      <View
        style={[
          styles.descriptionContainer,
          { backgroundColor: theme.colors.card },
        ]}
      >
        <Text style={[styles.description, { color: theme.colors.text }]}>
          {selectedCategory.root_node?.description ||
            "Sin descripción disponible"}
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  contentContainer: {
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    marginBottom: 16,
    textAlign: "center",
  },
  descriptionContainer: {
    padding: 16,
    borderRadius: 12,
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  description: {
    fontSize: 16,
    lineHeight: 24,
  },
  errorText: {
    fontSize: 16,
    textAlign: "center",
    marginTop: 20,
  },
});
