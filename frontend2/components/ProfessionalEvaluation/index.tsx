import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { theme } from "@/src/theme";
import { Category } from "@/app/types/category";
import { useCategories } from "@/app/contexts/categories";

export const ProfessionalEvaluation = () => {
  const { selectedCategory } = useCategories();

  if (!selectedCategory) return null;

  return (
    <View style={styles.container}>
      <Text style={styles.dataText}>Evaluación Profesional</Text>
      <Text style={styles.dataText}>{selectedCategory.name}</Text>
      <Text style={styles.dataText}></Text>
      <Text style={styles.dataText}>
        {JSON.stringify(
          selectedCategory.professional_evaluation_results || "{}"
        ) || "No hay resultados de evaluación"}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 16,
    backgroundColor: "white",
    borderRadius: 8,
    marginVertical: 8,
  },
  content: {
    gap: 8,
  },
  dataText: {
    fontSize: 16,
  },
  recommendationsText: {
    fontSize: 16,
    fontStyle: "italic",
    marginTop: 8,
  },
  professionalText: {
    fontSize: 14,
    color: "#666",
    marginTop: 8,
  },
  dateText: {
    fontSize: 12,
    color: "#999",
  },
});
