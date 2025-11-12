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
            size={theme.typography.sizes.headline1}
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
          <Ionicons
            name="school-outline"
            size={theme.typography.sizes.headline1}
            color={theme.colors.text}
          />
          <Text style={[styles.actionButtonText, { color: theme.colors.text }]}>
            {/* Ir a Entrenamiento */}
            Ir a Contenido
          </Text>
        </TouchableOpacity>
      </View>

      {/* <View style={styles.statusContainer}> */}
      <View>
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
    fontSize: theme.typography.sizes.display3,
    fontWeight: "bold",
    marginBottom: theme.typography.sizes.body2,
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
    fontSize: theme.typography.sizes.body1,
    lineHeight: theme.typography.sizes.subtitle,
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
    fontSize: theme.typography.sizes.body1,
    fontWeight: "600",
    textAlign: "center",
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
    fontSize: theme.typography.sizes.title,
    fontWeight: "600",
    marginBottom: 8,
  },
  statusText: {
    fontSize: theme.typography.sizes.body1,
    marginBottom: theme.typography.sizes.body2,
  },
  recommendationsContainer: {
    marginTop: 16,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
    paddingTop: 16,
  },
  recommendationsTitle: {
    fontSize: theme.typography.sizes.subtitle,
    fontWeight: "600",
    marginBottom: 8,
  },
  recommendationsText: {
    fontSize: theme.typography.sizes.body1,
    lineHeight: theme.typography.sizes.subtitle,
  },
  errorText: {
    fontSize: theme.typography.sizes.body1,
    textAlign: "center",
    marginTop: 20,
  },
});
