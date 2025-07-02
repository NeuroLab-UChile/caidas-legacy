import { useState, useEffect, useCallback, useRef } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Image,
} from "react-native";
import { useCategories } from "../contexts/categories";
import { Button, LoadingIndicator } from "@/components/Common";
import { CategoryHeader } from "@/components/CategoryHeader";
import { useRouter } from "expo-router";
import ActivityNodeContainer from "@/components/ActivityNodes/ActivityNodeContainer";
import Ionicons from "@expo/vector-icons/Ionicons";
import { Ionicons as ExpoIonicons } from "@expo/vector-icons";
import { router } from "expo-router";

import { ActivityNodeType } from "@/components/ActivityNodes";
import EmptyState from "../containers/EmptyState";
import { DoctorRecommendations } from "@/components/DoctorRecommendations";
import { getCategoryStatus } from "@/utils/categoryHelpers";
import { VideoView, useVideoPlayer } from "expo-video";
import { useEventListener } from "expo";
import * as FileSystem from "expo-file-system";
import { theme } from "@/src/theme";
import { VideoPlayerView } from "@/components/VideoPlayer";
import { useFocusEffect } from "@react-navigation/native";
import { apiService } from "@/app/services/apiService";

type TrainingState = {
  currentNodeId: number | null;
  history: number[];
  trainingResult: {
    initial_node_id: number | null;
    nodes: any[];
  };
};

const TrainingScreen = () => {
  const { selectedCategory, fetchCategories } = useCategories();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState<"training" | "recommendations" | null>(null);

  useFocusEffect(
    useCallback(() => {
      apiService.activityLog.trackAction("screen entrenar"); // Record action
    }, [])
  );

  const [trainingState, setTrainingState] = useState<TrainingState>(() => {
    const nodes = selectedCategory?.training_form?.training_nodes || [];
    if (nodes.length === 0) {
      console.log("No hay nodos de entrenamiento disponibles");
      return {
        currentNodeId: null,
        history: [],
        trainingResult: {
          initial_node_id: null,
          nodes: [],
        },
      };
    }

    return {
      currentNodeId: nodes[0]?.id || null,
      history: [],
      trainingResult: {
        initial_node_id: nodes[0]?.id || null,
        nodes: nodes,
      },
    };
  });
  const [videoError, setVideoError] = useState<string | null>(null);
  const [showVideo, setShowVideo] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [history, setHistory] = useState<number[]>([]);
  const nodes = selectedCategory?.training_form?.training_nodes || [];
  const currentQuestionIndex = nodes.findIndex(
    (node) => node.id === trainingState.currentNodeId
  );

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

  useEffect(() => {
    if (selectedCategory?.recommendations?.video_url) {
      prepareVideo(selectedCategory.recommendations.video_url);
    }
  }, [selectedCategory?.recommendations?.video_url]);

  useEffect(() => {
    if (selectedCategory?.training_form?.training_nodes) {
      console.log("=== TRAINING NODES DETAILS ===");
      selectedCategory.training_form.training_nodes.forEach((node, index) => {
        console.log(`Node elisa ${index + 1}:`, {
          node,
        });
      });
      console.log("Current Node ID:", trainingState.currentNodeId);
      console.log("History:", trainingState.history);
      console.log("========================");
    }
  }, [selectedCategory, trainingState]);

  useEffect(() => {
    console.log("Estado inicial:", {
      selectedCategory,
      trainingNodes: selectedCategory?.training_form?.training_nodes,
      currentNodeId: trainingState.currentNodeId,
      view,
    });
  }, [selectedCategory, trainingState.currentNodeId, view]);

  useEffect(() => {
    if (selectedCategory?.training_form?.training_nodes) {
      const nodes = selectedCategory.training_form.training_nodes;
      console.log(
        "Actualizando trainingState por cambio en selectedCategory:",
        nodes
      );

      setTrainingState({
        currentNodeId: nodes[0]?.id || null,
        history: [],
        trainingResult: {
          initial_node_id: nodes[0]?.id || null,
          nodes: nodes,
        },
      });
    }
  }, [selectedCategory]);

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
    (nodeId: number | null) => {
      const node =
        selectedCategory?.training_form?.training_nodes.find(
          (node) => node.id === nodeId
        ) || null;

      console.log("Getting current node:", {
        requestedId: nodeId,
        foundNode: node,
        availableNodes: selectedCategory?.training_form?.training_nodes.map(
          (n) => ({
            id: n.id,
            type: n.type,
          })
        ),
      });

      return node;
    },
    [selectedCategory]
  );

  const handleNext = useCallback(
    (response?: any) => {
      console.log("Handling next with current state:", {
        currentNodeId: trainingState.currentNodeId,
        history: trainingState.history,
        response,
      });

      setTrainingState((prev) => {
        const currentNode = getCurrentNode(prev.currentNodeId);
        console.log("Current node for navigation:", currentNode);

        // Encontrar el índice del nodo actual
        const currentIndex =
          selectedCategory?.training_form?.training_nodes.findIndex(
            (node) => node.id === prev.currentNodeId
          );

        // Obtener el siguiente nodo
        const nextNode =
          currentIndex !== undefined
            ? selectedCategory?.training_form?.training_nodes[currentIndex + 1]
            : undefined;
        console.log("Next node:", nextNode);

        if (nextNode) {
          return {
            ...prev,
            currentNodeId: nextNode.id,
            history: [...prev.history, prev.currentNodeId!],
          };
        } else {
          console.log("No more nodes available");
          return {
            ...prev,
            currentNodeId: null,
          };
        }
      });
    },
    [selectedCategory, getCurrentNode]
  );

  const handleNodeResponse = (nodeId: number, response: any) => {
    console.log("Node response:", { nodeId, response });
    handleNext(response);
  };
  const handleNavigateBefore = () => {
    console.log("Navegando hacia atrás. Índice actual:", currentQuestionIndex);
    if (currentQuestionIndex > 0) {
      const previousNode = nodes[currentQuestionIndex - 1];
      console.log("Nodo anterior:", previousNode);
      if (previousNode) {
        // Actualizar el estado con el nodo anterior y mantener las respuestas existentes
        setTrainingState((prev) => ({
          ...prev,
          currentNodeId: previousNode.id,
          // Mantener las respuestas existentes
          history: prev.history.filter((r) => r !== prev.currentNodeId),
        }));
      }
    }
  };

  const renderNode = (nodeId: number | null) => {
    const node = getCurrentNode(nodeId);
    if (!node) return null;

    return (
      <ActivityNodeContainer
        type={node.type as ActivityNodeType}
        data={node}
        onNext={(response: any) => handleNodeResponse(node.id, response)}
        onBack={handleBack}
        onBefore={handleNavigateBefore}
        categoryId={selectedCategory?.id}
        responses={[]}
        currentQuestionIndex={currentQuestionIndex}
        totalQuestions={nodes.length}
      />
    );
  };

  const prepareVideo = async (remoteUrl: string) => {
    try {
      // Crear directorio de caché si no existe
      const cacheDir = `${FileSystem.cacheDirectory}videos/`;
      const dirInfo = await FileSystem.getInfoAsync(cacheDir);
      if (!dirInfo.exists) {
        await FileSystem.makeDirectoryAsync(cacheDir, { intermediates: true });
      }

      // Crear un nombre de archivo único para el video
      const filename = remoteUrl.split("/").pop() || "video.mp4";
      const localUri = `${cacheDir}${filename}`;

      // Verificar si ya existe en caché
      const info = await FileSystem.getInfoAsync(localUri);

      if (!info.exists) {
        // Descargar el video si no está en caché
        const downloadResumable = FileSystem.createDownloadResumable(
          remoteUrl,
          localUri,
          {}
        );

        try {
          const downloadResult = await downloadResumable.downloadAsync();
          if (!downloadResult?.uri) {
            throw new Error("No se pudo obtener la URI del video descargado");
          }
        } catch (downloadError) {
          throw new Error(`Error al descargar: ${downloadError}`);
        }
      }
    } catch (error) {
      setVideoError(`Error al preparar el video: ${error}`);
    }
  };

  const renderVideo = () => {
    if (!selectedCategory?.recommendations?.video_url) {
      return null;
    }

    return (
      <VideoPlayerView
        url={selectedCategory.recommendations.video_url}
        description={selectedCategory.recommendations.text}
      />
    );
  };

  const renderDoctorReview = () => {
    console.log("Rendering doctor review:", selectedCategory?.recommendations);

    if (!selectedCategory?.recommendations) {
      return (
        <View style={styles.emptyStateContainer}>
          <Ionicons name="document-text-outline" size={48} color="#9CA3AF" />
          <Text style={styles.emptyStateText}>
            No hay recomendaciones disponibles
            {/* #TODO: MEJORAR TEXTO CUANDO NO HAY RECOMENDACIONES */}
          </Text>
        </View>
      );
    }

    const { status, text, video_url, updated_at, professional } =
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

            {renderVideo()}

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

  const handleBack = () => {
    if (view) {
      setView(null);
    } else {
      router.push("/(tabs)/action");
    }
  };

  if (loading) return <LoadingIndicator />;
  if (!selectedCategory) return <EmptyState view="training" />;

  return (
    <ScrollView style={styles.container}>
      <CategoryHeader
        name={selectedCategory?.name || "Categoría no seleccionada"}
      />

      <TouchableOpacity style={styles.backButton} onPress={handleBack}>
        <Ionicons name="chevron-back" size={24} color={theme.colors.text} />
        <Text style={styles.backButtonText}>
          {view ? "Volver" : "Volver al inicio"}
        </Text>
      </TouchableOpacity>

      {!view && (
        <View style={styles.viewSelection}>
          {selectedCategory?.recommendations && (
            <TouchableOpacity
              style={styles.optionCard}
              onPress={() => {
                console.log("Abriendo recomendaciones");
                apiService.activityLog.trackAction(
                  `open_recommendations ${selectedCategory.id}`
                ); // Record action
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
            onPress={() => {
              apiService.activityLog.trackAction(
                `open_training ${selectedCategory.id}`
              ); // Record action
              setView("training");
            }}
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
          {!selectedCategory?.training_form?.training_nodes ? (
            <View style={styles.errorContainer}>
              <Text>No hay nodos de entrenamiento configurados</Text>
            </View>
          ) : selectedCategory.training_form.training_nodes.length === 0 ? (
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
          ) : !trainingState.currentNodeId ? (
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
          ) : (
            renderNode(trainingState.currentNodeId)
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
    marginBottom: 40,
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
    marginBottom: 40,
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
    padding: 12,
    marginBottom: 16,
  },
  backButtonText: {
    marginLeft: 8,
    fontSize: 16,
    color: theme.colors.text,
    fontFamily: "System",
    fontWeight: "600",
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
    backgroundColor: "#f0f0f0",
  },
  video: {
    width: "100%",
    height: "100%",
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  loadingText: {
    marginTop: 8,
    color: "#666",
    fontSize: 14,
  },
  errorContainer: {
    padding: 20,
    alignItems: "center",
    justifyContent: "center",
  },
  errorText: {
    color: "red",
    fontSize: 16,
  },
  retryText: {
    color: "white",
    marginTop: 8,
  },
  thumbnailContainer: {
    width: "100%",
    height: "100%",
    justifyContent: "center",
    alignItems: "center",
  },
  playButtonOverlay: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "rgba(0,0,0,0.3)",
  },
  playButtonText: {
    fontSize: 40,
  },
  videoWrapper: {
    position: "relative",
    width: "100%",
    height: "100%",
  },
  loadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "rgba(0,0,0,0.5)",
  },
});
export default TrainingScreen;
