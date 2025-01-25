import React from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from "react-native";
import { useCategories } from "../contexts/categories";
import { theme } from "@/src/theme";
import { useRouter } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { getCategoryStatus } from "@/utils/categoryHelpers";

export default function CategoryDetailScreen() {
  const { selectedCategory } = useCategories();
  const router = useRouter();

  if (!selectedCategory) {
    return (
      <View style={styles.container}>
        <Text style={[styles.errorText, { color: theme.colors.text }]}>
          No hay categoría seleccionada
        </Text>
      </View>
    );
  }

  const status = getCategoryStatus(selectedCategory);

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
          {selectedCategory.description || "Sin descripción disponible"}
        </Text>
      </View>

      <View style={styles.actionsContainer}>
        <TouchableOpacity
          style={[
            styles.actionButton,
            { backgroundColor: theme.colors.primary },
          ]}
          onPress={() => router.push("/evaluate")}
        >
          <Ionicons
            name="clipboard-outline"
            size={24}
            color={theme.colors.text}
          />
          <Text style={[styles.actionButtonText, { color: theme.colors.text }]}>
            Ir a mi Evaluación
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[
            styles.actionButton,
            { backgroundColor: theme.colors.primary },
          ]}
          onPress={() => router.push("/training")}
        >
          <Ionicons name="school-outline" size={24} color={theme.colors.text} />
          <Text style={[styles.actionButtonText, { color: theme.colors.text }]}>
            Ir a Entrenamiento
          </Text>
        </TouchableOpacity>
      </View>

      <View style={styles.statusContainer}>
        <Text style={[styles.statusTitle, { color: theme.colors.text }]}>
          Estado de la Evaluación
        </Text>
        <Text style={[styles.statusText, { color: theme.colors.text }]}>
          {status?.text || "Estado desconocido"}
        </Text>
        {selectedCategory.professional_recommendations && (
          <View style={styles.recommendationsContainer}>
            <Text
              style={[
                styles.recommendationsTitle,
                { color: theme.colors.text },
              ]}
            >
              Recomendaciones del Doctor
            </Text>
            <Text
              style={[styles.recommendationsText, { color: theme.colors.text }]}
            >
              {selectedCategory.professional_recommendations}
            </Text>
          </View>
        )}
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
    gap: 16,
  },
  title: {
    fontSize: 28,
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
    marginBottom: 24,
  },
  description: {
    fontSize: 16,
    lineHeight: 24,
  },
  actionsContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    gap: 12,
    marginBottom: 24,
  },
  actionButton: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    padding: 16,
    borderRadius: 12,
    gap: 8,
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  actionButtonText: {
    fontSize: 16,
    fontWeight: "600",
  },
  statusContainer: {
    backgroundColor: theme.colors.card,
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
  statusTitle: {
    fontSize: 20,
    fontWeight: "600",
    marginBottom: 8,
  },
  statusText: {
    fontSize: 16,
    marginBottom: 16,
  },
  recommendationsContainer: {
    marginTop: 16,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
    paddingTop: 16,
  },
  recommendationsTitle: {
    fontSize: 18,
    fontWeight: "600",
    marginBottom: 8,
  },
  recommendationsText: {
    fontSize: 16,
    lineHeight: 24,
  },
  errorText: {
    fontSize: 16,
    textAlign: "center",
    marginTop: 20,
  },
});
