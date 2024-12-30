import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { theme } from "@/src/theme";
import { Category } from "@/app/types/category";

interface ProfessionalEvaluationProps {
  category: Category;
}

export const ProfessionalEvaluation: React.FC<ProfessionalEvaluationProps> = ({
  category,
}) => {
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Evaluación Profesional</Text>
        <Text style={styles.subtitle}>Resultados de la evaluación</Text>
      </View>

      <View style={styles.resultContainer}>
        {category.professional_evaluation_result ? (
          <>
            <Text style={styles.resultTitle}>Diagnóstico</Text>
            <Text style={styles.resultText}>
              {category.professional_evaluation_result}
            </Text>
          </>
        ) : (
          <Text style={styles.pendingText}>
            Pendiente de evaluación profesional
          </Text>
        )}
      </View>

      {category.professional_recommendations && (
        <View style={styles.recommendationsContainer}>
          <Text style={styles.recommendationsTitle}>
            Recomendaciones Profesionales
          </Text>
          <Text style={styles.recommendationsText}>
            {category.professional_recommendations}
          </Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: theme.colors.card,
    borderRadius: 16,
    padding: 20,
    margin: 16,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  header: {
    marginBottom: 20,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
    paddingBottom: 15,
  },
  title: {
    fontSize: 24,
    fontWeight: "700",
    color: theme.colors.text,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    fontWeight: "500",
  },
  resultContainer: {
    backgroundColor: theme.colors.background,
    borderRadius: 12,
    padding: 16,
    marginBottom: 20,
  },
  resultTitle: {
    fontSize: 18,
    fontWeight: "600",
    color: theme.colors.text,
    marginBottom: 12,
  },
  resultText: {
    fontSize: 16,
    color: theme.colors.text,
    lineHeight: 24,
  },
  pendingText: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    fontStyle: "italic",
    textAlign: "center",
  },
  recommendationsContainer: {
    backgroundColor: theme.colors.background,
    borderRadius: 12,
    padding: 16,
  },
  recommendationsTitle: {
    fontSize: 18,
    fontWeight: "600",
    color: theme.colors.text,
    marginBottom: 12,
  },
  recommendationsText: {
    fontSize: 16,
    color: theme.colors.text,
    lineHeight: 24,
  },
});
