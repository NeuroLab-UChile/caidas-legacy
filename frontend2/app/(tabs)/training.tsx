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
import { DoctorRecommendations } from "@/components/DoctorRecommendations";
import { getCategoryStatus } from "@/utils/categoryHelpers";
import { Video } from "expo-av";

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

  useEffect(() => {
    const categoryWithoutIcon = { ...selectedCategory };
    delete categoryWithoutIcon.icon;
    console.log("Category without icon:", categoryWithoutIcon);
  }, [selectedCategory]);

  useEffect(() => {
    console.log("Vista actual:", view);
    if (view === "recommendations") {
      console.log("Datos de recomendaciones:", {
        hasCategory: !!selectedCategory,
        recommendations: selectedCategory?.recommendations,
        text: selectedCategory?.recommendations?.text,
        status: selectedCategory?.recommendations?.status,
      });
    }
  }, [view, selectedCategory]);

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

  const renderDoctorReview = () => {
    console.log("Rendering doctor review:", selectedCategory?.recommendations);

    if (!selectedCategory?.recommendations) {
      return (
        <View style={styles.emptyStateContainer}>
          <Ionicons name="document-text-outline" size={48} color="#9CA3AF" />
          <Text style={styles.emptyStateText}>
            No hay recomendaciones disponibles
          </Text>
        </View>
      );
    }

    const { status, text, media_url, updated_at, professional } =
      selectedCategory.recommendations;

    return (
      <ScrollView style={styles.recommendationsContainer}>
        <View style={styles.recommendationsCard}>
          <View style={styles.recommendationsHeader}>
            <View style={styles.iconContainer}>
              <Ionicons name="medical" size={32} color="#4CAF50" />
            </View>
            <Text style={styles.recommendationsTitle}>
              Recomendaciones Médicas
            </Text>
          </View>

          {professional?.name && (
            <View style={styles.professionalContainer}>
              <View style={styles.professionalHeader}>
                <Ionicons name="person" size={20} color="#4B5563" />
                <Text style={styles.professionalName}>{professional.name}</Text>
              </View>
              {professional.role && (
                <Text style={styles.professionalRole}>{professional.role}</Text>
              )}
            </View>
          )}

          {status && (
            <View style={styles.statusContainer}>
              <View
                style={[
                  styles.statusDot,
                  { backgroundColor: status.color || "#808080" },
                ]}
              />
              <Text style={styles.statusText}>
                {status.text || "Estado no definido"}
              </Text>
            </View>
          )}

          <View style={styles.recommendationContent}>
            <View style={styles.recommendationTextContainer}>
              <Text
                style={[
                  styles.recommendationText,
                  !text && { fontStyle: "italic" },
                ]}
              >
                {text || "No hay recomendaciones específicas en este momento."}
              </Text>
            </View>

            {media_url && (
              <View style={styles.videoContainer}>
                <Video
                  source={{ uri: media_url }}
                  useNativeControls
                  resizeMode="contain"
                  shouldPlay={false}
                  style={styles.video}
                  onError={(error) => {
                    console.error("Error loading video:", error);
                  }}
                />
              </View>
            )}

            {updated_at && (
              <Text style={styles.updatedAtText}>
                Actualizado: {new Date(updated_at).toLocaleDateString()}
              </Text>
            )}
          </View>

          <TouchableOpacity
            style={styles.backButton}
            onPress={() => setView(null)}
          >
            <Ionicons name="arrow-back" size={24} color="white" />
            <Text style={styles.backButtonText}>Volver al Menú</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    );
  };

  if (loading) return <LoadingIndicator />;
  if (!selectedCategory) return <EmptyState view="training" />;

  return (
    <ScrollView style={styles.container}>
      <CategoryHeader name={selectedCategory.name} />
      {!view && (
        <View style={styles.viewSelection}>
          {selectedCategory?.recommendations && (
            <TouchableOpacity
              style={styles.optionCard}
              onPress={() => {
                console.log("Abriendo recomendaciones");
                setView("recommendations");
              }}
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
      {view === "recommendations" && renderDoctorReview()}
      {view === "training" && (
        <>
          {selectedCategory.training_form?.training_nodes?.length === 0 ? (
            <View style={styles.completedContainer}>
              <View style={styles.completedCard}>
                <View style={styles.completedIconContainer}>
                  <Ionicons name="fitness-outline" size={80} color="#9CA3AF" />
                </View>
                <Text style={styles.completedTitle}>
                  Sin Entrenamiento Disponible
                </Text>
                <Text style={styles.completedDescription}>
                  No hay ejercicios configurados para esta categoría.
                </Text>

                <TouchableOpacity
                  style={styles.backToMenuButton}
                  onPress={() => setView(null)}
                >
                  <Ionicons name="arrow-back" size={24} color="#4B5563" />
                  <Text style={styles.backToMenuText}>Volver al Menú</Text>
                </TouchableOpacity>
              </View>
            </View>
          ) : trainingState.currentNodeId ? (
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
    fontSize: 18,
    fontWeight: "700",
    color: "#1F2937",
    marginLeft: 12,
    flexWrap: "wrap",
    textAlign: "center",
  },
  recommendationContent: {
    backgroundColor: "#F8FAF9",
    borderRadius: 16,
    padding: 20,
    marginVertical: 10,
  },
  recommendationSection: {
    marginBottom: 24,
  },
  recommendationSectionTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#374151",
    marginBottom: 12,
  },
  divider: {
    height: 1,
    backgroundColor: "#E5E7EB",
    marginVertical: 20,
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
    alignItems: "center",
    padding: 20,
  },
  emptyStateText: {
    fontSize: 16,
    color: "#9CA3AF",
    marginTop: 8,
    textAlign: "center",
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
  statusContainer: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 16,
    backgroundColor: "white",
    padding: 12,
    borderRadius: 8,
    flexWrap: "wrap",
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  statusText: {
    fontSize: 14,
    color: "#6B7280",
  },
  recommendationText: {
    fontSize: 16,
    color: "#374151",
    lineHeight: 24,
    marginTop: 8,
    flexWrap: "wrap",
  },
  updatedAtText: {
    fontSize: 12,
    color: "#9CA3AF",
    fontStyle: "italic",
  },
  professionalContainer: {
    backgroundColor: "white",
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  professionalHeader: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 4,
  },
  professionalName: {
    fontSize: 14,
    fontWeight: "500",
    color: "#374151",
    marginLeft: 8,
    flex: 1,
  },
  professionalRole: {
    fontSize: 13,
    color: "#4B5563",
    marginTop: 4,
    marginLeft: 24,
    fontStyle: "italic",
  },
  dateText: {
    fontSize: 12,
    color: "#9CA3AF",
    marginTop: 8,
    marginLeft: 24,
  },
  dotSeparator: {
    marginHorizontal: 8,
  },
  recommendationTextContainer: {
    backgroundColor: "white",
    padding: 16,
    borderRadius: 8,
  },
  videoContainer: {
    marginTop: 16,
    width: "100%",
    aspectRatio: 16 / 9,
    borderRadius: 8,
    overflow: "hidden",
  },
  video: {
    width: "100%",
    height: "100%",
  },
});
export default TrainingScreen;
