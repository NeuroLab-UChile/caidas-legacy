import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { theme } from "@/src/theme";
import { useCategories } from "@/app/contexts/categories";
import { formatDate } from "date-fns";
import { Ionicons } from "@expo/vector-icons";

export const ProfessionalEvaluation = () => {
  const { selectedCategory } = useCategories();
  const evaluationForm = selectedCategory?.evaluation_form;
  const professional = selectedCategory?.recommendations?.professional;

  const isCompleted = !!evaluationForm?.completed_date;

  const renderProfessionalInfo = () => {
    if (!isCompleted) {
      return (
        <View style={styles.pendingContainer}>
          <View style={styles.iconContainer}>
            <Ionicons name="medical" size={32} color={theme.colors.warning} />
          </View>
          <Text style={styles.pendingTitle}>Pendiente de Evaluación</Text>
          <Text style={styles.pendingDescription}>
            Esta evaluación debe ser realizada por un profesional de la salud.
            Por favor, agenda una cita para completarla.
          </Text>
        </View>
      );
    }

    const { diagnosis, observations } =
      evaluationForm.professional_responses || {};
    const professional_name = professional?.name;
    const professional_role = professional?.role;
    const evaluation_date = evaluationForm.completed_date;

    return (
      <View style={styles.completedContainer}>
        <View style={styles.headerSection}>
          <View style={styles.successIconContainer}>
            <Ionicons
              name="checkmark-circle"
              size={32}
              color={theme.colors.success}
            />
          </View>
          <Text style={styles.completedTitle}>Evaluación Completada</Text>
        </View>

        <View style={styles.infoCard}>
          {/* Información del Profesional */}
          <View style={styles.professionalSection}>
            <View style={styles.professionalHeader}>
              <Ionicons
                name="person"
                size={24}
                color={theme.colors.textSecondary}
              />
              <View style={styles.professionalInfo}>
                <Text style={styles.professionalName}>{professional_name}</Text>
                {professional_role && (
                  <Text style={styles.professionalRole}>
                    {professional_role}
                  </Text>
                )}
              </View>
            </View>
            {evaluation_date && (
              <Text style={styles.evaluationDate}>
                Evaluado el{" "}
                {formatDate(new Date(evaluation_date), "dd/MM/yyyy")}
              </Text>
            )}
          </View>

          {/* Diagnóstico y Observaciones */}
          <View style={styles.evaluationDetails}>
            {diagnosis && (
              <View style={styles.detailSection}>
                <View style={styles.detailHeader}>
                  <Ionicons
                    name="fitness"
                    size={20}
                    color={theme.colors.textSecondary}
                  />
                  <Text style={styles.detailLabel}>Diagnóstico</Text>
                </View>
                <Text style={styles.detailValue}>{diagnosis}</Text>
              </View>
            )}

            {observations && (
              <View style={styles.detailSection}>
                <View style={styles.detailHeader}>
                  <Ionicons
                    name="clipboard"
                    size={20}
                    color={theme.colors.textSecondary}
                  />
                  <Text style={styles.detailLabel}>Observaciones</Text>
                </View>
                <Text style={styles.detailValue}>{observations}</Text>
              </View>
            )}
          </View>
        </View>
      </View>
    );
  };

  return <View style={styles.container}>{renderProfessionalInfo()}</View>;
};

const styles = StyleSheet.create({
  container: {
    padding: 16,
    backgroundColor: theme.colors.background,
  },
  pendingContainer: {
    backgroundColor: theme.colors.card,
    borderRadius: 16,
    padding: 24,
    alignItems: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  iconContainer: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: `${theme.colors.warning}15`,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 16,
  },
  pendingTitle: {
    fontSize: 20,
    fontWeight: "700",
    color: theme.colors.text,
    marginBottom: 12,
    textAlign: "center",
  },
  pendingDescription: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    textAlign: "center",
    lineHeight: 24,
  },
  completedContainer: {
    gap: 16,
  },
  headerSection: {
    alignItems: "center",
    marginBottom: 8,
  },
  successIconContainer: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: `${theme.colors.success}15`,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 12,
  },
  completedTitle: {
    fontSize: 20,
    fontWeight: "700",
    color: theme.colors.success,
    textAlign: "center",
  },
  infoCard: {
    backgroundColor: theme.colors.card,
    borderRadius: 16,
    padding: 20,
    gap: 20,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  professionalSection: {
    borderBottomWidth: 1,
    borderBottomColor: `${theme.colors.border}50`,
    paddingBottom: 16,
  },
  professionalHeader: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 8,
  },
  professionalInfo: {
    marginLeft: 12,
    flex: 1,
  },
  professionalName: {
    fontSize: 18,
    fontWeight: "600",
    color: theme.colors.text,
  },
  professionalRole: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginTop: 2,
  },
  evaluationDate: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginTop: 4,
  },
  evaluationDetails: {
    gap: 16,
  },
  detailSection: {
    gap: 8,
  },
  detailHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  detailLabel: {
    fontSize: 16,
    fontWeight: "600",
    color: theme.colors.text,
  },
  detailValue: {
    fontSize: 16,
    color: theme.colors.text,
    backgroundColor: theme.colors.background,
    padding: 12,
    borderRadius: 12,
    lineHeight: 24,
  },
});
