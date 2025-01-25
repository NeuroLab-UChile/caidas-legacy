// frontend2/app/(tabs)/evaluate.tsx
import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
} from "react-native";
import { useCategories } from "../contexts/categories";
import { theme } from "@/src/theme";
import { Category, QuestionNode } from "@/app/types/category";

import apiService from "../services/apiService";
import { getCategoryStatus } from "@/utils/categoryHelpers";
import { CategoryHeader } from "@/components/CategoryHeader";

import { ActivityNodeType } from "@/components/ActivityNodes";
import ActivityNodeContainer from "@/components/ActivityNodes/ActivityNodeContainer";
import { DoctorRecommendations } from "@/components/DoctorRecommendations";
import { router } from "expo-router";
import EmptyState from "../containers/EmptyState";
import { useAuth } from "../contexts/auth";
import { UserProfile } from "../services/apiService";
import { ProfessionalEvaluation } from "@/components/ProfessionalEvaluation";

interface NodeResponse {
  nodeId: number;
  response: FormattedResponse;
}

interface FormattedResponse {
  id: number;
  type: ActivityNodeType;
  question: string;
  metadata: {
    timestamp: string;
    version: string;
  };
  answer: any; // Tipo específico según el tipo de nodo
}

interface EvaluationState {
  currentNodeId: number | null;
  responses: NodeResponse[];
  completed: boolean;
  history: number[];
  evaluationResult: {
    initial_node_id: number | null;
    nodes: QuestionNode[];
  };
}

const getWelcomeText = (category: Category) => {
  if (category.evaluation_type.type === "PROFESSIONAL") {
    return {
      title: "Evaluación Profesional",
      description:
        category.description ||
        "Esta evaluación será realizada por un profesional de la salud.",

      note: "Agenda una cita con tu profesional de salud para realizar esta evaluación.",
      buttonText: "Ver Evaluación",
    };
  }

  return {
    title: "Autoevaluación",
    description:
      category.description ||
      "Esta evaluación nos ayudará a entender mejor tu estado de salud.",

    note: "Toma unos minutos para responder con sinceridad.",
    buttonText: "Comenzar Evaluación",
  };
};

const WelcomeScreen = ({
  category,
  onStart,
  userName,
}: {
  category: Category;
  onStart: () => void;
  userName: string;
}) => {
  const welcomeText = getWelcomeText(category);

  return (
    <View style={styles.welcomeContainer}>
      <Text style={styles.welcomeTitle}>¡Hola {userName}!</Text>

      <Text style={styles.welcomeSubtitle}>
        Bienvenido a la evaluación de {category.name}
      </Text>

      <Text style={styles.welcomeDescription}>{welcomeText.description}</Text>

      {welcomeText.note && (
        <Text style={styles.noteText}>{welcomeText.note}</Text>
      )}

      <TouchableOpacity style={styles.startButton} onPress={onStart}>
        <Text style={styles.startButtonText}>{welcomeText.buttonText}</Text>
      </TouchableOpacity>
    </View>
  );
};

const initializeEvaluationState = (
  category: Category | null
): EvaluationState => {
  // Si es evaluación profesional, no necesitamos inicializar nodos
  if (category?.evaluation_type?.type === "PROFESSIONAL") {
    return {
      currentNodeId: null,
      responses: [],
      completed: false,
      history: [],
      evaluationResult: {
        initial_node_id: null,
        nodes: [],
      },
    };
  }

  const nodes = category?.evaluation_form?.question_nodes || [];
  const existingResponses = Object.entries(
    category?.evaluation_form?.responses || {}
  ).map(
    ([key, value]): NodeResponse => ({
      nodeId: parseInt(key),
      response: value,
    })
  );

  return {
    currentNodeId: nodes[0]?.id || null,
    responses: existingResponses,
    completed: Boolean(category?.evaluation_form?.completed_date),
    history: [],
    evaluationResult: {
      initial_node_id: nodes[0]?.id || null,
      nodes,
    },
  };
};

const EvaluateScreen = () => {
  const { selectedCategory, fetchCategories } = useCategories();
  const { userProfile } = useAuth();

  const [loading, setLoading] = useState(false);
  const [showWelcome, setShowWelcome] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const [evaluationState, setEvaluationState] = useState<EvaluationState>(() =>
    initializeEvaluationState(selectedCategory)
  );

  useEffect(() => {
    const refreshData = async () => {
      setLoading(true);
      try {
        await fetchCategories();
      } catch (error) {
        console.error("Error refreshing categories:", error);
      } finally {
        setLoading(false);
      }
    };

    refreshData();
  }, []);

  useEffect(() => {
    if (selectedCategory) {
      const isProfessional =
        selectedCategory.evaluation_type?.type === "PROFESSIONAL";
      const newState = initializeEvaluationState(selectedCategory);

      setEvaluationState(newState);

      // Corregir la condición para mostrar la pantalla de bienvenida
      setShowWelcome(
        !isProfessional &&
          (!selectedCategory.evaluation_form?.completed_date ||
            selectedCategory.evaluation_form?.responses === null ||
            Object.keys(selectedCategory.evaluation_form?.responses || {})
              .length === 0)
      );
    }
  }, [selectedCategory]);

  const handleStartNewEvaluation = () => {
    Alert.alert(
      "Nueva Evaluación",
      "¿Estás seguro de que deseas iniciar una nueva evaluación? Se eliminarán las recomendaciones anteriores.",
      [
        {
          text: "Cancelar",
          style: "cancel",
        },
        {
          text: "Sí, iniciar",
          onPress: async () => {
            try {
              setLoading(true);

              if (selectedCategory?.id) {
                // Limpiar las respuestas en el backend
                await apiService.categories.saveResponses(
                  selectedCategory.id,
                  new FormData()
                );

                // Reiniciar el estado local
                const nodes =
                  selectedCategory?.evaluation_form?.question_nodes || [];
                setEvaluationState({
                  currentNodeId: nodes[0]?.id || null,
                  responses: [],
                  completed: false,
                  history: [],
                  evaluationResult: {
                    initial_node_id: nodes[0]?.id || null,
                    nodes,
                  },
                });

                // Mostrar la pantalla de bienvenida
                renderContent();
              }
            } catch (error) {
              console.error("Error al iniciar nueva evaluación:", error);
              Alert.alert("Error", "No se pudo iniciar una nueva evaluación");
            } finally {
              setLoading(false);
            }
          },
        },
      ]
    );
  };

  const getNextNodeId = (currentNodeId: number): number | null => {
    const nodes = selectedCategory?.evaluation_form?.question_nodes || [];
    if (!nodes || nodes.length === 0) {
      return null;
    }
    const currentIndex = nodes.findIndex((node) => node.id === currentNodeId);

    if (currentIndex === -1 || currentIndex === nodes.length - 1) {
      return null;
    }

    return nodes[currentIndex + 1].id;
  };

  const formatNodeResponse = (node: QuestionNode, response: any) => {
    const baseResponse = {
      id: node.id,
      type: node.type,
      question: node.question,
      metadata: {
        timestamp: new Date().toISOString(),
        version: "1.0",
      },
    };

    // Manejar cada tipo de respuesta de forma segura
    const answerMap: Record<ActivityNodeType, (res: any) => any> = {
      SINGLE_CHOICE_QUESTION: (res) => ({
        selectedOption: res.selectedOption,
        options: node.options || [],
      }),
      MULTIPLE_CHOICE_QUESTION: (res) => ({
        selectedOptions: res.selectedOptions || [],
        options: node.options || [],
      }),
      TEXT_QUESTION: (res) => ({
        value: res.answer || "",
      }),
      IMAGE_QUESTION: (res) => ({
        images: res.answer || [],
      }),
      SCALE_QUESTION: (res) => ({
        value: res?.answer?.value || res?.value || 0,
      }),
      DESCRIPTION_NODE: function (res: any) {
        throw new Error("Function not implemented.");
      },
      VIDEO_NODE: function (res: any) {
        throw new Error("Function not implemented.");
      },
      IMAGE_NODE: function (res: any) {
        throw new Error("Function not implemented.");
      },
      TEXT_NODE: function (res: any) {
        throw new Error("Function not implemented.");
      },
      WEEKLY_RECIPE_NODE: function (res: any) {
        throw new Error("Function not implemented.");
      },
      RESULT_NODE: function (res: any) {
        throw new Error("Function not implemented.");
      },
    };

    const formatter = answerMap[node.type];
    if (!formatter) {
      console.warn(`Tipo de nodo no manejado: ${node.type}`);
      return { ...baseResponse, answer: response };
    }

    return {
      ...baseResponse,
      answer: formatter(response),
    };
  };

  const handleNodeResponse = async (nodeId: number, response: any) => {
    try {
      const node = getCurrentNode(nodeId);
      if (!node) throw new Error("Nodo no encontrado");

      const formattedResponse = formatNodeResponse(node, response);
      const newResponses = {
        ...Object.fromEntries(
          evaluationState.responses.map((r) => [r.nodeId, r.response])
        ),
        [nodeId]: formattedResponse,
      };

      const nextNodeId = getNextNodeId(nodeId);
      const isCompleted =
        !nextNodeId ||
        Object.keys(newResponses).length ===
          selectedCategory?.evaluation_form?.question_nodes.length;

      if (isCompleted && selectedCategory?.id) {
        setLoading(true);
        try {
          const formData = new FormData();

          // Agregar las respuestas como JSON string
          const responsesObj: Record<string, any> = {};
          Object.entries(newResponses).forEach(([key, value]) => {
            responsesObj[key] = value;
          });
          formData.append("responses", JSON.stringify(responsesObj));

          // Procesar imágenes si existen
          Object.entries(newResponses).forEach(
            ([key, value]: [string, any]) => {
              if (value.type === "IMAGE_QUESTION" && value.answer?.images) {
                value.answer.images.forEach(
                  (imageUri: string, index: number) => {
                    // Crear un nombre único para cada imagen
                    const imageName = `image_${key}_${index}.jpg`;

                    // Agregar la imagen al FormData con el nombre correcto
                    formData.append(`image_${key}`, {
                      uri: imageUri,
                      type: "image/jpeg",
                      name: imageName,
                    } as any);
                  }
                );
              }
            }
          );

          console.log(
            "Enviando FormData con imágenes:",
            Array.from(formData.entries()).map(([key, value]) => ({
              key,
              type: value instanceof File ? "File" : typeof value,
            }))
          );

          await apiService.categories.saveResponses(
            selectedCategory.id,
            formData
          );
          await fetchCategories();

          setEvaluationState({
            currentNodeId: null,
            responses: Object.entries(newResponses).map(([key, value]) => ({
              nodeId: parseInt(key),
              response: value as NodeResponse["response"],
            })),
            completed: true,
            history: [],
            evaluationResult: {
              initial_node_id: null,
              nodes: selectedCategory?.evaluation_form?.question_nodes || [],
            },
          });

          Alert.alert("Éxito", "Evaluación guardada correctamente");
        } catch (error) {
          console.error("Error saving responses:", error);
          Alert.alert("Error", "No se pudo guardar la evaluación");
        } finally {
          setLoading(false);
        }
      } else {
        setEvaluationState((prev) => ({
          ...prev,
          responses: Object.entries(newResponses).map(([key, value]) => ({
            nodeId: parseInt(key),
            response: value as NodeResponse["response"],
          })),
          currentNodeId: nextNodeId,
          completed: false,
          history: [...prev.history, nodeId],
        }));
      }
    } catch (error) {
      console.error("Error en handleNodeResponse:", error);
      Alert.alert("Error", `No se pudo procesar la respuesta: ${error}`);
    }
  };

  useEffect(() => {
    if (selectedCategory) {
      const { icon, ...categoryWithoutIcon } = selectedCategory;
    }
  }, [selectedCategory]);

  const getCurrentNode = (nodeId: number | null): QuestionNode | null => {
    const nodes = selectedCategory?.evaluation_form?.question_nodes || [];
    if (!nodeId || !nodes || nodes.length === 0) {
      return null;
    }
    return nodes.find((node) => node.id === nodeId) || null;
  };

  const renderNode = (nodeId: number | null, handleBack: () => void) => {
    const node = getCurrentNode(nodeId);
    if (!node) return null;

    return (
      <ActivityNodeContainer
        type={node.type}
        data={node}
        onNext={(response: any) => handleNodeResponse(node.id, response)}
        onBack={handleBack}
        categoryId={selectedCategory?.id}
        responses={evaluationState.responses}
      />
    );
  };

  const renderDoctorReview = () => {
    if (!selectedCategory?.recommendations) return null;

    const { status, text, professional, updated_at } =
      selectedCategory.recommendations;

    if (!status || !text) {
      return (
        <View style={{ padding: 16 }}>
          <Text>Espera a que el doctor revise tu evaluación</Text>
        </View>
      );
    }

    return (
      <DoctorRecommendations
        status={status}
        recommendations={text}
        professional={professional || { name: "", role: "" }}
        updatedAt={updated_at || ""}
      />
    );
  };

  const onRefresh = React.useCallback(async () => {
    setRefreshing(true);
    try {
      await fetchCategories();
    } catch (error) {
      console.error("Error refreshing categories:", error);
    } finally {
      setRefreshing(false);
    }
  }, [fetchCategories]);

  const renderContent = () => {
    if (!selectedCategory) return null;
    if (selectedCategory.evaluation_type.type === "PROFESSIONAL") {
      return <ProfessionalEvaluation />;
    }

    if (evaluationState.completed) {
      const status = getCategoryStatus(selectedCategory);
      return (
        <View style={styles.completedContainer}>
          <Text
            style={[styles.completedText, { color: status?.color || "#000" }]}
          >
            {status?.text || "✅ Evaluación Completada"}
          </Text>
          {renderDoctorReview()}
          <TouchableOpacity
            style={[styles.startButton, { marginTop: 24 }]}
            onPress={handleStartNewEvaluation}
          >
            <Text style={styles.startButtonText}>Iniciar Nueva Evaluación</Text>
          </TouchableOpacity>
        </View>
      );
    }

    // Para evaluaciones no completadas
    if (showWelcome) {
      return (
        <WelcomeScreen
          category={selectedCategory}
          userName={
            userProfile?.first_name || userProfile?.username || "Usuario"
          }
          onStart={() => setShowWelcome(false)}
        />
      );
    }

    // Renderizar nodos de evaluación
    return renderNode(evaluationState.currentNodeId, () => {
      if (evaluationState.history.length > 0) {
        const previousNodes = [...evaluationState.history];
        const previousNodeId = previousNodes.pop();
        setEvaluationState((prev) => ({
          ...prev,
          currentNodeId: previousNodeId || null,
          history: previousNodes,
        }));
      }
    });
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <Text>Cargando...</Text>
      </View>
    );
  }

  if (!selectedCategory) {
    return <EmptyState view="evaluate" />;
  }

  return (
    <View style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.contentContainer}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {selectedCategory && (
          <CategoryHeader name={selectedCategory.name || ""} />
        )}
        {renderContent()}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  contentContainer: {
    padding: 16,
    paddingBottom: 100,
  },
  completedContainer: {
    alignItems: "center",
    padding: 24,
    backgroundColor: theme.colors.card,
    borderRadius: 16,
    margin: 16,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  completedText: {
    fontSize: 22,
    fontWeight: "700",
    color: theme.colors.text,
    marginBottom: 12,
    textAlign: "center",
  },
  startButton: {
    backgroundColor: theme.colors.primary,
    padding: 16,
    borderRadius: 12,
    width: "100%",
    alignItems: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 4,
  },
  startButtonText: {
    color: theme.colors.text,
    fontSize: 18,
    fontWeight: "600",
  },
  welcomeContainer: {
    backgroundColor: theme.colors.card,
    borderRadius: 16,
    padding: 24,
    margin: 16,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  welcomeTitle: {
    fontSize: 28,
    fontWeight: "700",
    color: theme.colors.text,
    marginBottom: 8,
    textAlign: "center",
  },
  welcomeSubtitle: {
    fontSize: 20,
    fontWeight: "600",
    color: theme.colors.text,
    marginBottom: 16,
    textAlign: "center",
  },
  welcomeDescription: {
    fontSize: 16,
    color: theme.colors.text,
    marginBottom: 12,
  },
  bulletPoints: {
    marginBottom: 24,
  },
  bulletPoint: {
    fontSize: 16,
    color: theme.colors.text,
    marginBottom: 8,
    lineHeight: 24,
  },
  noteText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    fontStyle: "italic",
    marginBottom: 24,
    textAlign: "center",
  },
});

export default EvaluateScreen;
