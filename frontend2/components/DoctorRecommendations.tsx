import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { theme } from "@/src/theme";
import { formatDate } from "date-fns";

interface DoctorRecommendationsProps {
  status: {
    color: string;
    text: string;
  };
  recommendations: string;
  professional: {
    name: string;
    role: string;
  };
  updatedAt: string;
}

export const DoctorRecommendations: React.FC<DoctorRecommendationsProps> = ({
  status,
  recommendations,
  professional,
  updatedAt,
}) => {
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.statusContainer}>
          <View
            style={[
              styles.statusDot,
              {
                backgroundColor:
                  status?.color === "green"
                    ? "#28a745"
                    : status?.color || "#gray",
              },
            ]}
          />
          <Text style={styles.statusText}>{status?.text || "Sin evaluar"}</Text>
        </View>
      </View>

      <View style={styles.recommendationsContainer}>
        <Text style={styles.recommendationsTitle}>
          Recomendaciones médicas:
        </Text>
        <Text style={styles.recommendationsText}>
          {recommendations || "Sin recomendaciones"}
        </Text>
      </View>

      {professional.name && (
        <View style={styles.updateInfo}>
          <Text style={styles.updateInfoText}>
            Actualizado por: {professional.name}
          </Text>
          {updatedAt && (
            <Text style={styles.updateInfoText}>Fecha: {updatedAt}</Text>
          )}
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    width: "100%",
    padding: 16,
    backgroundColor: theme.colors.card,
    borderRadius: 12,
    marginVertical: 8,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 16,
  },
  statusContainer: {
    flexDirection: "row",
    alignItems: "center",
  },
  statusDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  statusLabel: {
    fontSize: 16,
    color: theme.colors.textSecondary,
  },
  statusText: {
    fontSize: 16,
    fontWeight: "600",
    color: theme.colors.text,
  },
  recommendationsContainer: {
    marginTop: 8,
  },
  recommendationsTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: theme.colors.text,
    marginBottom: 8,
  },
  recommendationsText: {
    fontSize: 14,
    color: theme.colors.text,
    lineHeight: 20,
  },
  updateInfo: {
    marginTop: 16,
    padding: 12,
    backgroundColor: theme.colors.surface,
    borderRadius: 8,
  },
  updateInfoText: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    marginBottom: 4,
  },
});
