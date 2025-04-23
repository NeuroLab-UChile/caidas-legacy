// frontend2/app/(tabs)/evaluate.tsx
import { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
  Platform,
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
import React from "react";
import { Ionicons } from '@expo/vector-icons';
import { format } from "date-fns";
import { es } from "date-fns/locale";

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

interface Status {
  color: string;
  text: string;
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
  const [history, setHistory] = useState<number[]>([]);

  const [evaluationState, setEvaluationState] = useState<EvaluationState>(() =>
    initializeEvaluationState(selectedCategory)
  );

  const status = selectedCategory?.recommendations?.status as Status | undefined;

  const nodes = selectedCategory?.evaluation_form?.question_nodes || [];
  const currentQuestionIndex = nodes.findIndex(node => node.id === evaluationState.currentNodeId);

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
    const nodes = selectedCategory?.evaluation_form?.question_nodes || [];

    if (nodes.length === 0) {
      Alert.alert("Error", "No hay preguntas disponibles para esta evaluación");
      return;
    }

    Alert.alert(
      "Iniciar Nueva Evaluación",
      "¿Estás seguro de que deseas iniciar una nueva evaluación? La evaluación anterior quedará guardada.",
      [
        {
          text: "Cancelar",
          style: "cancel",
        },
        {
          text: "Iniciar",
          style: "default",
          onPress: async () => {
            setEvaluationState({
              currentNodeId: nodes[0]?.id || null,
              responses: [],
              completed: false,
              history: [],
              evaluationResult: {
                initial_node_id: nodes[0]?.id || null,
                nodes: nodes,
              },
            });

            // Resetear el historial
            setHistory([]);
            if (selectedCategory?.id) {
              await apiService.evaluations.clearAndStartNew(
                selectedCategory.id,
              );
            }
          },
        },
      ],
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

  const handleNavigateBack = () => {
    // Solo para el botón de Salir
    Alert.alert(
      "",
      selectedCategory?.evaluation_type?.type === "PROFESSIONAL"
        ? "¿Finalizar evaluación?"
        : "¿Finalizar entrenamiento?",
      [
        { text: "Cancelar", style: "cancel" },
        {
          text: "Finalizar",
          style: "destructive",
          onPress: () => router.push("/(tabs)/action"),
        },
      ],
    );
  };

  const handleNavigateBefore = () => {
    console.log("Navegando hacia atrás. Índice actual:", currentQuestionIndex);
    if (currentQuestionIndex > 0) {
      const previousNode = nodes[currentQuestionIndex - 1];
      console.log("Nodo anterior:", previousNode);
      if (previousNode) {
        // Actualizar el estado con el nodo anterior y mantener las respuestas existentes
        setEvaluationState((prev) => ({
          ...prev,
          currentNodeId: previousNode.id,
          // Mantener las respuestas existentes
          responses: prev.responses.filter(
            (r) => r.nodeId !== prev.currentNodeId,
          ),
        }));
      }
    }
  };

  const handleNodeResponse = async (nodeId: number, response: any) => {
    try {
      const node = getCurrentNode(nodeId);
      if (!node) throw new Error("Nodo no encontrado");

      const formattedResponse = formatNodeResponse(node, response);

      // Actualizar las respuestas manteniendo el formato correcto
      const newResponses = [
        ...evaluationState.responses.filter((r) => r.nodeId !== nodeId),
        { nodeId, response: formattedResponse },
      ];

      const nextNodeId = getNextNodeId(nodeId);
      const isCompleted = !nextNodeId || newResponses.length === nodes.length;

      if (isCompleted && selectedCategory?.id) {
        setLoading(true);
        try {
          const formData = new FormData();

          // Convertir las respuestas al formato esperado por el API
          const responsesObj = newResponses.reduce(
            (acc, curr) => {
              acc[curr.nodeId] = curr.response;
              return acc;
            },
            {} as Record<string, any>,
          );

          formData.append("responses", JSON.stringify(responsesObj));

          // Procesar imágenes si existen
          newResponses.forEach((nodeResponse) => {
            const response = nodeResponse.response;
            if (response.type === "IMAGE_QUESTION" && response.answer?.images) {
              response.answer.images.forEach(
                (imageUri: string, index: number) => {
                  const imageName = `image_${nodeResponse.nodeId}_${index}.jpg`;
                  formData.append(`image_${nodeResponse.nodeId}`, {
                    uri: imageUri,
                    type: "image/jpeg",
                    name: imageName,
                  } as any);
                },
              );
            }
          });

          await apiService.categories.saveResponses(
            selectedCategory.id,
            formData,
          );
          await fetchCategories();

          setEvaluationState({
            currentNodeId: null,
            responses: newResponses,
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
          responses: newResponses,
          currentNodeId: nextNodeId,
          completed: false,
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

  const renderNode = (nodeId: number | null) => {
    const node = getCurrentNode(nodeId);
    if (!node) return null;

    return (
      <ActivityNodeContainer
        type={node.type}
        data={node}
        onNext={(response: any) => handleNodeResponse(node.id, response)}
        onBefore={handleNavigateBefore}
        onBack={handleNavigateBack}
        categoryId={selectedCategory?.id}
        responses={evaluationState.responses}
        currentQuestionIndex={currentQuestionIndex}
        totalQuestions={nodes.length}
        nodeType={
          selectedCategory?.evaluation_type?.type === "PROFESSIONAL"
            ? "evaluation"
            : "training"
        }
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

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return format(date, "dd/MM/yyyy HH:mm", { locale: es });
    } catch (error) {
      return dateString;
    }
  };

  const renderCompletedEvaluation = () => {
    const updatedBy =
      selectedCategory?.recommendations?.professional?.name || "Sistema";
    const updatedDate = selectedCategory?.evaluation_form?.completed_date;

    return (
      <View style={styles.completedContainer}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => router.push("/(tabs)/action")}
        >
          <Ionicons name="chevron-back" size={24} color={theme.colors.text} />
          <Text style={styles.backButtonText}>Volver al inicio</Text>
        </TouchableOpacity>

        <View style={styles.resultCard}>
          <View style={styles.statusContainer}>
            <View
              style={[
                styles.statusIndicator,
                { backgroundColor: status?.color || theme.colors.success },
              ]}
            />
            <Text style={[styles.statusText, { color: theme.colors.text }]}>
              {status?.text || "Poco Riesgoso"}
            </Text>
          </View>

          <View style={styles.recommendationsContainer}>
            <Text style={styles.recommendationsTitle}>
              Recomendaciones médicas:
            </Text>
            <Text style={styles.recommendationsText}>
              {selectedCategory?.recommendations?.text ||
                "Su hogar presenta medidas previas de mitigación de riesgos. Reevalúe áreas clave para mantener la seguridad."}
            </Text>
          </View>

          <View style={styles.separator} />

          <View style={styles.metadataContainer}>
            <View style={styles.metadataRow}>
              <Text style={styles.metadataLabel}>Actualizado por</Text>
              <Text style={styles.metadataValue}>{updatedBy}</Text>
            </View>
            <View style={styles.metadataRow}>
              <Text style={styles.metadataLabel}>Fecha</Text>
              <Text style={styles.metadataValue}>
                {updatedDate ? formatDate(updatedDate) : "-"}
              </Text>
            </View>
          </View>

          <TouchableOpacity
            style={styles.newEvaluationButton}
            onPress={handleStartNewEvaluation}
          >
            <Text style={styles.newEvaluationButtonText}>
              Iniciar Nueva Evaluación
            </Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  };

  const renderContent = () => {
    if (!selectedCategory) return null;

    if (selectedCategory.evaluation_type.type === "PROFESSIONAL") {
      return (
        <View>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => router.push("/(tabs)/action")}
          >
            <Ionicons name="chevron-back" size={24} color={theme.colors.text} />
            <Text style={styles.backButtonText}>Volver al inicio</Text>
          </TouchableOpacity>
          <ProfessionalEvaluation />
        </View>
      );
    }

    if (!evaluationState.currentNodeId || evaluationState.completed) {
      return renderCompletedEvaluation();
    }

    return renderNode(evaluationState.currentNodeId);
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
    flex: 1,
    padding: 16,
  },
  resultCard: {
    backgroundColor: theme.colors.card,
    borderRadius: 24,
    padding: 24,
    marginTop: 16,
    ...Platform.select({
      ios: {
        shadowColor: "#000",
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.1,
        shadowRadius: 12,
      },
      android: {
        elevation: 4,
      },
    }),
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 24,
  },
  statusIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  statusText: {
    fontSize: 24,
    fontWeight: '600',
    color: theme.colors.text,
  },
  recommendationsContainer: {
    marginTop: 24,
  },
  recommendationsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.textSecondary,
    marginBottom: 12,
  },
  recommendationsText: {
    fontSize: 16,
    color: theme.colors.text,
    lineHeight: 24,
  },
  separator: {
    height: 1,
    backgroundColor: theme.colors.border,
    marginVertical: 24,
  },
  metadataContainer: {
    backgroundColor: `${theme.colors.background}80`,
    borderRadius: 12,
    padding: 16,
  },
  metadataRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  metadataLabel: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  metadataValue: {
    fontSize: 14,
    color: theme.colors.text,
    fontWeight: '500',
  },
  newEvaluationButton: {
    backgroundColor: theme.colors.primary,
    borderRadius: 16,
    padding: 16,
    alignItems: 'center',
    marginTop: 24,
    ...Platform.select({
      ios: {
        shadowColor: theme.colors.primary,
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.2,
        shadowRadius: 8,
      },
      android: {
        elevation: 4,
      },
    }),
  },
  newEvaluationButtonText: {
    color: theme.colors.text,
    fontSize: 16,
    fontWeight: '600',
  },
  startButton: {
    backgroundColor: theme.colors.primary,
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 16,
  },
  startButtonText: {
    color: theme.colors.background,
    fontSize: 16,
    fontWeight: '600',
  },
  backButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
  },
  backButtonText: {
    marginLeft: 8,
    fontSize: 16,
    color: theme.colors.text,
  },
  noEvaluationContainer: {
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
  noEvaluationText: {
    fontSize: 18,
    color: theme.colors.textSecondary,
    textAlign: "center",
    marginTop: 16,
    marginBottom: 8,
  },
  startText: {
    fontSize: 18,
    color: theme.colors.text,
    textAlign: 'center',
    marginVertical: 16,
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
