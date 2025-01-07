import React from "react";
import { View, Text, StyleSheet, Platform } from "react-native";
import { theme } from "@/src/theme";
import { useCategories } from "@/app/contexts/categories";
import { format } from "date-fns";
import { es } from "date-fns/locale";
import Ionicons from "@expo/vector-icons/Ionicons";

export const ProfessionalEvaluation = () => {
  const { selectedCategory } = useCategories();
  const evaluationForm = selectedCategory?.evaluation_form;
  const recommendations = selectedCategory?.recommendations;
  const statusColor = recommendations?.status?.color || theme.colors.success;

  const { diagnosis, observations } =
    evaluationForm?.professional_responses || {};
  const professional = recommendations?.professional;
  const evaluation_date = evaluationForm?.completed_date;

  const formatDate = (date: string) => {
    return format(new Date(date), "d 'de' MMMM, yyyy", { locale: es });
  };

  const getCardStyle = (index: number) => [
    styles.card,
    {
      borderLeftColor: statusColor,
      borderLeftWidth: 4,
      shadowColor: statusColor,
    },
  ];

  return (
    <View style={styles.container}>
      <View style={[styles.gradientBackground]}>
        <View style={styles.content}>
          {/* Header */}
          <View style={styles.header}>
            <View
              style={[
                styles.iconContainer,
                { backgroundColor: `${statusColor}15` },
              ]}
            >
              <Ionicons
                name="checkmark-circle"
                size={32}
                color={theme.colors.text}
              />
            </View>
            <Text style={styles.title}>Evaluación Profesional</Text>
            <Text style={styles.subtitle}>
              {recommendations?.status?.text || "Estado de la evaluación"}
            </Text>
          </View>

          {/* Professional Info Card */}
          {professional && (
            <View style={getCardStyle(0)}>
              <View style={styles.cardHeader}>
                <Ionicons name="person" size={20} color={theme.colors.text} />
                <Text style={styles.cardHeaderText}>
                  Información del Profesional
                </Text>
              </View>
              <Text style={styles.professionalInfo}>
                <Text style={styles.boldText}>{professional.name}</Text>
                {professional.role && (
                  <Text style={styles.roleText}> - {professional.role}</Text>
                )}
              </Text>
              {evaluation_date && (
                <Text style={styles.dateText}>
                  Evaluado el {formatDate(evaluation_date)}
                </Text>
              )}
            </View>
          )}

          {/* Diagnosis Card */}
          {diagnosis && (
            <View style={getCardStyle(1)}>
              <View style={styles.cardHeader}>
                <Ionicons name="medical" size={20} color={theme.colors.text} />
                <Text style={styles.cardHeaderText}>Diagnóstico</Text>
              </View>
              <Text style={styles.diagnosisText}>{diagnosis}</Text>
            </View>
          )}

          {/* Observations Card */}
          {observations && (
            <View style={getCardStyle(2)}>
              <View style={styles.cardHeader}>
                <Ionicons
                  name="clipboard"
                  size={20}
                  color={theme.colors.text}
                />
                <Text style={styles.cardHeaderText}>Observaciones</Text>
              </View>
              <Text style={styles.observationsText}>{observations}</Text>
            </View>
          )}

          {/* Color Indicator */}
          {recommendations?.status?.color && (
            <View style={styles.colorIndicator}>
              <Text style={styles.colorText}>
                Color de recomendación profesional:
              </Text>
              <View
                style={[styles.colorSquare, { backgroundColor: statusColor }]}
              />
            </View>
          )}
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  gradientBackground: {
    flex: 1,
    paddingHorizontal: 16,
    paddingTop: 24,
    paddingBottom: 32,
  },
  content: {
    gap: 16,
  },
  header: {
    alignItems: "center",
    marginBottom: 24,
  },
  iconContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: "bold",
    textAlign: "center",
    marginBottom: 8,
    color: theme.colors.text,
  },
  subtitle: {
    fontSize: 18,
    color: theme.colors.textSecondary,
    textAlign: "center",
  },
  card: {
    backgroundColor: "#FFFFFF",
    borderRadius: 16,
    padding: 20,
    ...Platform.select({
      ios: {
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.15,
        shadowRadius: 8,
        shadowColor: "#000",
      },
      android: {
        elevation: 8,
      },
    }),
  },
  cardHeader: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 12,
  },
  cardHeaderText: {
    fontSize: 18,
    fontWeight: "600",
    marginLeft: 8,
    color: theme.colors.text,
  },
  professionalInfo: {
    fontSize: 16,
    color: theme.colors.text,
    marginBottom: 4,
  },
  boldText: {
    fontWeight: "600",
  },
  roleText: {
    color: theme.colors.textSecondary,
  },
  dateText: {
    fontSize: 14,
    color: theme.colors.textTertiary,
    marginTop: 4,
  },
  diagnosisText: {
    fontSize: 16,
    color: theme.colors.text,
    lineHeight: 24,
  },
  observationsText: {
    fontSize: 16,
    color: theme.colors.text,
    fontStyle: "italic",
    lineHeight: 24,
  },
  colorIndicator: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    marginTop: 24,
    gap: 8,
  },
  colorText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  colorSquare: {
    width: 16,
    height: 16,
    borderRadius: 4,
  },
});
