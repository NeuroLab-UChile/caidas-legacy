import React, { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from "react-native";
import { useCategories } from "../contexts/categories";
import { Button, LoadingIndicator } from "@/components/Common";
import { CategoryHeader } from "@/components/CategoryHeader";
import { useRouter } from "expo-router";
import ActivityNodeContainer from "@/components/ActivityNodes/ActivityNodeContainer";
import Ionicons from "@expo/vector-icons/Ionicons";
import { TrainingState } from "../types/category";
import { ActivityNodeType } from "@/components/ActivityNodes";
import EmptyState from "../containers/EmptyState";

const TrainingScreen = () => {
  const { selectedCategory, fetchCategories } = useCategories();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState<"training" | "recommendations" | null>(null);
  const [trainingState, setTrainingState] = useState<TrainingState>(() => {
    const nodes = selectedCategory?.training_form?.training_nodes || [];
    return {
      currentNodeId: nodes[0]?.id || null,
      history: [],
      trainingResult: {
        initial_node_id: nodes[0]?.id || null,
        nodes: nodes,
      },
    };
  });

  useEffect(() => {
    fetchCategories();
  }, []);

  const handleRestart = useCallback(() => {
    const nodes = selectedCategory?.training_form?.training_nodes || [];
    setTrainingState({
      currentNodeId: nodes[0]?.id || null,
      history: [],
      trainingResult: {
        initial_node_id: nodes[0]?.id || null,
        nodes: nodes,
      },
    });
  }, [selectedCategory]);

  const getCurrentNode = useCallback(
    (nodeId: number | null) =>
      selectedCategory?.training_form?.training_nodes.find(
        (node) => node.id === nodeId
      ) || null,
    [selectedCategory]
  );

  const renderNode = useCallback(
    (nodeId: number | null) => {
      const node = getCurrentNode(nodeId);
      if (!node) return null;

      return (
        <ActivityNodeContainer
          type={node.type as ActivityNodeType}
          data={node}
          onNext={() => {
            const nodes = selectedCategory?.training_form?.training_nodes || [];
            const currentIndex = nodes.findIndex((n) => n.id === nodeId);
            const nextNodeId =
              currentIndex < nodes.length - 1
                ? nodes[currentIndex + 1].id
                : null;

            setTrainingState((prev) => ({
              ...prev,
              currentNodeId: nextNodeId,
              history: [...prev.history, node.id],
              trainingResult: {
                ...prev.trainingResult,
                nodes: prev.trainingResult.nodes,
              },
            }));
          }}
          onBack={() => {
            if (trainingState.history.length > 0) {
              const previousNodeId =
                trainingState.history[trainingState.history.length - 1];
              setTrainingState((prev) => ({
                ...prev,
                currentNodeId: previousNodeId,
                history: prev.history.slice(0, -1),
                trainingResult: {
                  ...prev.trainingResult,
                  nodes: prev.trainingResult.nodes,
                },
              }));
            } else {
              setView(null);
            }
          }}
          responses={{}}
          categoryId={selectedCategory?.id}
        />
      );
    },
    [getCurrentNode, trainingState, selectedCategory, setView]
  );

  if (loading) return <LoadingIndicator />;
  if (!selectedCategory) return <EmptyState view="training" />;

  return (
    <ScrollView style={styles.container}>
      <CategoryHeader name={selectedCategory.name} />
      {!view && (
        <View style={styles.viewSelection}>
          {selectedCategory.professional_recommendations && (
            <TouchableOpacity
              style={styles.optionCard}
              onPress={() => setView("recommendations")}
            >
              <View style={styles.iconContainer}>
                <Ionicons name="medical" size={32} color="#4CAF50" />
              </View>
              <Text style={styles.optionTitle}>
                Recomendaciones Personalizadas
              </Text>
              <Text style={styles.optionDescription}>
                Revisa las recomendaciones específicas de tu profesional de
                salud
              </Text>
            </TouchableOpacity>
          )}

          <TouchableOpacity
            style={styles.optionCard}
            onPress={() => setView("training")}
          >
            <View style={styles.iconContainer}>
              <Ionicons name="fitness" size={32} color="#2196F3" />
            </View>
            <Text style={styles.optionTitle}>Entrenamiento</Text>
            <Text style={styles.optionDescription}>
              Comienza tu rutina de ejercicios paso a paso
            </Text>
          </TouchableOpacity>
        </View>
      )}
      {view === "recommendations" && (
        <ScrollView style={styles.recommendationsContainer}>
          <View style={styles.recommendationsCard}>
            <View style={styles.recommendationsHeader}>
              <View style={styles.iconContainer}>
                <Ionicons name="medical" size={32} color="#4CAF50" />
              </View>
              <Text style={styles.recommendationsTitle}>
                Recomendación Médica
              </Text>
            </View>

            {selectedCategory.professional_recommendations ? (
              <View style={styles.recommendationContent}>
                <View style={styles.quoteIconContainer}>
                  <Ionicons name="chatbox-ellipses" size={24} color="#4CAF50" />
                </View>
                <Text style={styles.recommendationsText}>
                  "{selectedCategory.professional_recommendations}"
                </Text>
              </View>
            ) : (
              <View style={styles.emptyStateContainer}>
                <Ionicons
                  name="document-text-outline"
                  size={48}
                  color="#9CA3AF"
                />
                <Text style={styles.emptyStateText}>
                  No hay recomendaciones disponibles
                </Text>
              </View>
            )}

            <TouchableOpacity
              style={styles.backButton}
              onPress={() => setView(null)}
            >
              <Ionicons name="arrow-back" size={20} color="white" />
              <Text style={styles.backButtonText}>Volver</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      )}
      {view === "training" && (
        <>
          {trainingState.currentNodeId ? (
            renderNode(trainingState.currentNodeId)
          ) : (
            <View style={styles.completedContainer}>
              <View style={styles.completedCard}>
                <View style={styles.completedIconContainer}>
                  <Ionicons name="checkmark-circle" size={80} color="#4CAF50" />
                </View>
                <Text style={styles.completedTitle}>
                  ¡Entrenamiento Completado!
                </Text>
                <Text style={styles.completedDescription}>
                  Has finalizado todos los ejercicios. ¿Deseas realizarlos
                  nuevamente?
                </Text>

                <View style={styles.completedButtons}>
                  <TouchableOpacity
                    style={styles.restartButton}
                    onPress={handleRestart}
                  >
                    <Ionicons name="refresh" size={24} color="white" />
                    <Text style={styles.buttonText}>
                      Reiniciar Entrenamiento
                    </Text>
                  </TouchableOpacity>

                  <TouchableOpacity
                    style={styles.backToMenuButton}
                    onPress={() => setView(null)}
                  >
                    <Ionicons name="arrow-back" size={24} color="#4B5563" />
                    <Text style={styles.backToMenuText}>Volver al Menú</Text>
                  </TouchableOpacity>
                </View>
              </View>
            </View>
          )}
        </>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F5F6F8",
    padding: 16,
  },
  viewSelection: {
    marginTop: 24,
    gap: 16,
  },
  optionCard: {
    backgroundColor: "white",
    borderRadius: 16,
    padding: 20,
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  iconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: "#F5F6F8",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 16,
  },
  optionTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: "#1F2937",
    marginBottom: 8,
  },
  optionDescription: {
    fontSize: 14,
    color: "#6B7280",
    lineHeight: 20,
  },
  recommendationsContainer: {
    flex: 1,
    backgroundColor: "#F5F6F8",
  },
  recommendationsCard: {
    backgroundColor: "white",
    borderRadius: 20,
    margin: 16,
    padding: 20,
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
    minHeight: 300,
  },
  recommendationsHeader: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 20,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: "#E5E7EB",
  },

  recommendationsTitle: {
    fontSize: 20,
    fontWeight: "700",
    color: "#1F2937",
    flex: 1,
  },
  recommendationContent: {
    backgroundColor: "#F8FAF9",
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: "#E5E7EB",
    minHeight: 150,
    justifyContent: "center",
  },
  quoteIconContainer: {
    backgroundColor: "#E8F5E9",
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 16,
    alignSelf: "center",
  },
  recommendationsText: {
    fontSize: 16,
    color: "#374151",
    lineHeight: 24,
    textAlign: "center",
    fontStyle: "italic",
  },
  completedContainer: {
    flex: 1,
    padding: 16,
    backgroundColor: "#F5F6F8",
  },
  completedCard: {
    backgroundColor: "white",
    borderRadius: 20,
    padding: 24,
    alignItems: "center",
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  completedIconContainer: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: "#E8F5E9",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 24,
  },
  completedTitle: {
    fontSize: 24,
    fontWeight: "700",
    color: "#1F2937",
    marginBottom: 12,
    textAlign: "center",
  },
  completedDescription: {
    fontSize: 16,
    color: "#6B7280",
    textAlign: "center",
    marginBottom: 32,
    lineHeight: 24,
  },
  completedButtons: {
    width: "100%",
    gap: 16,
  },
  restartButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#4CAF50",
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    shadowColor: "#4CAF50",
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 4,
  },
  buttonText: {
    color: "white",
    fontSize: 16,
    fontWeight: "600",
    marginLeft: 8,
  },
  backToMenuButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#F3F4F6",
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
  },
  backToMenuText: {
    color: "#4B5563",
    fontSize: 16,
    fontWeight: "600",
    marginLeft: 8,
  },
  emptyStateContainer: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    padding: 20,
  },
  emptyStateText: {
    fontSize: 16,
    color: "#9CA3AF",
    marginTop: 8,
  },
  backButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#4CAF50",
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 12,
    shadowColor: "#4CAF50",
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 4,
  },
  backButtonText: {
    color: "white",
    fontSize: 16,
    fontWeight: "600",
    marginLeft: 8,
  },
});
export default TrainingScreen;
