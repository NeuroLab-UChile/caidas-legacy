import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { theme } from "@/src/theme";
import { formatDate } from "date-fns";

interface DoctorRecommendationsProps {
  statusColor: "green" | "yellow" | "red";
  recommendations: string;
  updatedBy?: {
    username: string;
    first_name: string;
    last_name: string;
  };
  updatedAt?: string;
}

export function DoctorRecommendations({
  statusColor,
  recommendations,
  updatedBy,
  updatedAt,
}: DoctorRecommendationsProps) {
  const statusColors = {
    green: theme.colors.success,
    yellow: theme.colors.warning,
    red: theme.colors.error,
  };

  const getStatusText = (color: string) => {
    switch (color) {
      case "green":
        return "✅ Evaluación Revisada: Estado Saludable";
      case "yellow":
        return "⚠️ Evaluación Revisada: Requiere Atención";
      case "red":
        return "🚨 Evaluación Revisada: Atención Urgente";
      default:
        return "Estado Desconocido";
    }
  };

  return (
    <View style={styles.cardContainer}>
      {/* Estado General */}
      <Text style={[styles.statusText, { color: statusColors[statusColor] }]}>
        {getStatusText(statusColor)}
      </Text>

      {/* Detalles del Estado */}
      <View style={styles.detailsContainer}>
        {updatedBy && (
          <Text style={styles.metaText}>
            Revisado por: Dr.{" "}
            {updatedBy.first_name
              ? `${updatedBy.first_name} ${updatedBy.last_name}`
              : updatedBy.username}
          </Text>
        )}
        {updatedAt && (
          <Text style={styles.metaText}>
            Fecha: {formatDate(updatedAt, "dd/MM/yyyy")}
          </Text>
        )}
      </View>

      {/* Recomendaciones */}
      <Text style={styles.recommendationsTitle}>Recomendaciones Médicas</Text>
      <Text style={styles.recommendationsText}>
        {recommendations || "Sin recomendaciones específicas."}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  cardContainer: {
    backgroundColor: theme.colors.card,
    borderRadius: 16,
    padding: 24,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.12,
    shadowRadius: 12,
    marginVertical: 16,
    width: "100%",
    elevation: 4,
  },
  statusText: {
    fontSize: 20,
    fontWeight: "800",
    textAlign: "center",
    marginBottom: 16,
    letterSpacing: 0.5,
  },
  detailsContainer: {
    marginBottom: 20,
    alignItems: "center",
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  metaText: {
    fontSize: 15,
    color: theme.colors.textSecondary,
    marginBottom: 4,
  },
  recommendationsTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: theme.colors.text,
    marginBottom: 12,
    textAlign: "left",
  },
  recommendationsText: {
    fontSize: 16,
    color: theme.colors.text,
    lineHeight: 24,
    textAlign: "left",
  },
});
