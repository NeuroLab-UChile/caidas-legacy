// frontend2/app/(tabs)/evaluate.tsx
import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
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

interface NodeResponse {
  nodeId: number;
  response: {
    selectedOption?: number;
    selectedOptions?: number[];
    answer?: string;
    value?: number;
  };
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

const EvaluateScreen = () => {
  const { selectedCategory, fetchCategories } = useCategories();
  const [loading, setLoading] = useState(false);

  // Añadir useEffect para actualizar datos al montar el componente
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
  }, []); // Se ejecuta al montar el componente

  // Añadir useEffect para actualizar el estado cuando cambie selectedCategory
  useEffect(() => {
    if (selectedCategory) {
      const nodes = selectedCategory.evaluation_form?.question_nodes || [];
      const existingResponses = Object.entries(
        selectedCategory.responses || {}
      ).map(
        ([key, value]): NodeResponse => ({
          nodeId: parseInt(key),
          response: value,
        })
      );

      const isFullyCompleted =
        selectedCategory.responses &&
        selectedCategory.evaluation_form?.question_nodes &&
        Object.keys(selectedCategory.responses || {}).length ===
          selectedCategory.evaluation_form.question_nodes.length;

      setEvaluationState({
        currentNodeId: Boolean(isFullyCompleted) ? null : nodes[0]?.id || null,
        responses: existingResponses,
        completed: Boolean(isFullyCompleted),
        history: [],
        evaluationResult: {
          initial_node_id: nodes[0]?.id || null,
          nodes: nodes,
        },
      });
    }
  }, [selectedCategory]); // Se ejecuta cuando cambia selectedCategory

  // Determinar si esta categoría específica está completada
  const hasDocterReview =
    selectedCategory?.status_color && selectedCategory?.doctor_recommendations;

  const hasCompletedEvaluation =
    selectedCategory?.responses &&
    selectedCategory?.evaluation_form?.question_nodes &&
    Object.keys(selectedCategory.responses || {}).length > 0;

  const isFullyCompleted =
    selectedCategory?.responses &&
    selectedCategory?.evaluation_form?.question_nodes &&
    Object.keys(selectedCategory.responses || {}).length ===
      selectedCategory.evaluation_form.question_nodes.length;
  const [evaluationState, setEvaluationState] = useState<EvaluationState>(
    () => {
      const nodes = selectedCategory?.evaluation_form?.question_nodes || [];
      const existingResponses = Object.entries(
        selectedCategory?.responses || {}
      ).map(
        ([key, value]): NodeResponse => ({
          nodeId: parseInt(key),
          response: value,
        })
      );

      return {
        currentNodeId: Boolean(isFullyCompleted) ? null : nodes[0]?.id || null,
        responses: existingResponses,
        completed: Boolean(isFullyCompleted),
        history: [],
        evaluationResult: {
          initial_node_id: nodes[0]?.id || null,
          nodes: nodes,
        },
      };
    }
  );

  const handleStartNewEvaluation = () => {
    // Reiniciar el estado local
    const nodes = selectedCategory?.evaluation_form?.question_nodes || [];

    setEvaluationState({
      currentNodeId: nodes[0]?.id || null,
      responses: [], // Reiniciar respuestas
      completed: false,
      history: [],
      evaluationResult: {
        initial_node_id: nodes[0]?.id || null,
        nodes: nodes,
      },
    });
  };

  const getNextNodeId = (currentNodeId: number): number | null => {
    if (!selectedCategory?.evaluation_form?.question_nodes) {
      return null;
    }

    const nodes = selectedCategory.evaluation_form.question_nodes;
    const currentIndex = nodes.findIndex((node) => node.id === currentNodeId);

    if (currentIndex === -1 || currentIndex === nodes.length - 1) {
      return null;
    }

    return nodes[currentIndex + 1].id;
  };

  const handleNodeResponse = async (nodeId: number, response: any) => {
    try {
      const node = getCurrentNode(nodeId);
      if (!node) {
        Alert.alert("Error", "Nodo no encontrado");
        return;
      }

      // Formato más completo de respuesta
      let formattedResponse = {
        id: nodeId,
        type: node.type,
        question: node.question,
        answer: null as any,
        metadata: {
          timestamp: new Date().toISOString(),
          version: "1.0",
        },
      };

      switch (node.type) {
        case "SINGLE_CHOICE_QUESTION":
          formattedResponse.answer = {
            selectedOption: response.selectedOption,
            options: node.options,
          };
          break;
        case "MULTIPLE_CHOICE_QUESTION":
          formattedResponse.answer = {
            selectedOptions: response.selectedOptions,
            options: node.options,
          };
          break;
        case "TEXT_QUESTION":
          console.log("response", response);
          formattedResponse.answer = {
            value: response.answer || "",
          };
          break;
        case "IMAGE_QUESTION":
          formattedResponse.answer = {
            image: response.image || "",
          };
          break;
        case "SCALE_QUESTION":
          formattedResponse.answer = {
            value: response.answer.value,
          };
          break;
        default:
          formattedResponse.answer = response;
      }

      // Obtener respuestas existentes y formatearlas
      const existingResponses = evaluationState.responses.reduce<
        Record<number, any>
      >((acc, curr) => {
        if (Object.keys(curr.response).length > 0) {
          acc[curr.nodeId] = curr.response;
        }
        return acc;
      }, {});

      const newResponses = {
        ...existingResponses,
        [nodeId]: formattedResponse,
      };

      const nextNodeId = getNextNodeId(nodeId);
      const isCompleted = !nextNodeId;

      if (isCompleted && selectedCategory?.id) {
        setLoading(true);
        console.log("newResponses", newResponses);
        try {
          await apiService.categories.saveResponses(
            selectedCategory.id,
            newResponses
          );

          await fetchCategories();

          setEvaluationState({
            currentNodeId: null,
            responses: Object.entries(newResponses).map(([key, value]) => ({
              nodeId: parseInt(key),
              response: value,
            })),
            completed: true,
            history: [],
            evaluationResult: {
              initial_node_id: null,
              nodes: selectedCategory?.evaluation_form?.question_nodes || [],
            },
          });

          Alert.alert("Éxito", "Evaluación guardada correctamente", [
            {
              text: "OK",
              onPress: async () => {
                await fetchCategories();
                setEvaluationState((prev) => ({ ...prev }));
              },
            },
          ]);
        } catch (error) {
          console.error("Error saving responses:", error);
          Alert.alert("Error", "No se pudo guardar la evaluación");
        } finally {
          setLoading(false);
        }
      } else {
        // Actualizar el estado solo con respuestas válidas
        setEvaluationState((prev) => ({
          ...prev,
          responses: Object.entries(newResponses).map(([key, value]) => ({
            nodeId: parseInt(key),
            response: value,
          })),
          currentNodeId: nextNodeId,
          completed: false,
          history: [...prev.history, nodeId],
        }));
      }
    } catch (error) {
      Alert.alert("Error", "No se pudo procesar la respuesta, " + error);
    }
  };

  const getCurrentNode = (nodeId: number | null): QuestionNode | null => {
    if (!nodeId || !selectedCategory?.evaluation_form?.question_nodes) {
      return null;
    }

    return (
      selectedCategory.evaluation_form.question_nodes.find(
        (node) => node.id === nodeId
      ) || null
    );
  };

  const renderNode = (nodeId: number | null, handleBack: () => void) => {
    const node = getCurrentNode(nodeId);
    if (!node) return null;

    return (
      <ActivityNodeContainer
        type={node.type as ActivityNodeType}
        data={node}
        onNext={(response: any) => handleNodeResponse(node.id, response)}
        onBack={handleBack}
        categoryId={selectedCategory?.id}
        responses={evaluationState.responses}
      />
    );
  };

  const renderDoctorReview = () => {
    if (!selectedCategory?.status_color) return null;

    return (
      <DoctorRecommendations
        statusColor={selectedCategory.status_color}
        recommendations={selectedCategory.doctor_recommendations || ""}
        updatedBy={selectedCategory.doctor_recommendations_updated_by}
        updatedAt={selectedCategory.doctor_recommendations_updated_at}
      />
    );
  };

  const renderResponsesList = () => {
    if (!selectedCategory?.responses) return null;

    try {
      const responsesArray = Object.values(selectedCategory.responses);

      return (
        <View style={styles.responsesList}>
          {responsesArray.map((response: any, index: number) => {
            // Validación de datos
            if (!response) return null;

            return (
              <View key={index} style={styles.responseItem}>
                <Text style={styles.questionText}>
                  {response.question || `Pregunta ${index + 1}`}
                </Text>
                <Text style={styles.answerText}>{renderAnswer(response)}</Text>
              </View>
            );
          })}
        </View>
      );
    } catch (error) {
      console.error("Error rendering responses:", error);
      return null;
    }
  };

  const renderAnswer = (response: any): string => {
    try {
      if (!response.answer) return "Sin respuesta";

      switch (response.type) {
        case "SCALE_QUESTION":
          return String(response.answer.value || "Sin valor");

        case "SINGLE_CHOICE_QUESTION":
          return String(
            response.answer.selectedOption !== undefined
              ? `Opción ${response.answer.selectedOption + 1}`
              : "Sin selección"
          );

        case "TEXT_QUESTION":
          return String(response.answer.value || "Sin texto");

        default:
          return String(response.answer || "Sin respuesta");
      }
    } catch (error) {
      console.error("Error rendering answer:", error);
      return "Error al mostrar respuesta";
    }
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
      >
        {selectedCategory && <CategoryHeader name={selectedCategory.name} />}

        {evaluationState.completed ? (
          <View style={styles.completedContainer}>
            <Text style={styles.completedText}>
              {getCategoryStatus(selectedCategory)?.text ||
                "✅ Evaluación Completada"}
            </Text>
            {hasDocterReview ? (
              <>
                <Text style={styles.infoText}>
                  El doctor ha revisado tus respuestas
                </Text>
                {renderDoctorReview()}
              </>
            ) : (
              <Text style={styles.infoText}>
                El doctor no ha revisado tus respuestas
              </Text>
            )}
            {renderResponsesList()}
            <TouchableOpacity
              style={[styles.startButton, { marginTop: 24 }]}
              onPress={handleStartNewEvaluation}
            >
              <Text style={styles.startButtonText}>
                Iniciar Nueva Evaluación
              </Text>
            </TouchableOpacity>
          </View>
        ) : (
          renderNode(evaluationState.currentNodeId, () => {
            if (evaluationState.history.length > 0) {
              const previousNodes = [...evaluationState.history];
              const previousNodeId = previousNodes.pop();
              setEvaluationState((prev) => ({
                ...prev,
                currentNodeId: previousNodeId || null,
                history: previousNodes,
              }));
            }
          })
        )}
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
    paddingBottom: 100, // Espacio extra para el botón flotante
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
  infoText: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    textAlign: "center",
    marginBottom: 24,
    lineHeight: 22,
  },
  responsesList: {
    width: "100%",
    backgroundColor: theme.colors.background,
    borderRadius: 12,
    marginTop: 24,
  },
  responseItem: {
    marginBottom: 20,
    padding: 16,
    backgroundColor: theme.colors.card,
    borderRadius: 12,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  questionText: {
    fontSize: 16,
    fontWeight: "600",
    color: theme.colors.text,
    marginBottom: 8,
  },
  answerText: {
    fontSize: 15,
    color: theme.colors.textSecondary,
    marginLeft: 16,
    lineHeight: 22,
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
});

export default EvaluateScreen;
