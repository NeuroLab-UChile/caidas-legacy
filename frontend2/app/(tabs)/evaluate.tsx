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
import { renderActivityNode } from "@/utils/nodeRenderers";
import { ActivityNodeType } from "@/components/ActivityNodes";
import ActivityNodeContainer from "@/components/ActivityNodes/ActivityNodeContainer";

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

  useEffect(() => {
    if (selectedCategory) {
      const status = getCategoryStatus(selectedCategory);
      const nodes = selectedCategory.evaluation_form?.question_nodes || [];
      const existingResponses = selectedCategory.responses || {};
      const isCompleted =
        status?.status === "completed" || status?.status === "reviewed";

      setEvaluationState({
        currentNodeId: isCompleted ? null : nodes[0]?.id || null,
        responses: Object.entries(existingResponses).map(
          ([key, value]): NodeResponse => ({
            nodeId: parseInt(key),
            response: value,
          })
        ),
        completed: isCompleted,
        history: [],
        evaluationResult: {
          initial_node_id: nodes[0]?.id || null,
          nodes: nodes,
        },
      });
    }
  }, [selectedCategory]);

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
        question: node.data.question,
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
            options: node.data.options,
          };
          break;
        case "MULTIPLE_CHOICE_QUESTION":
          formattedResponse.answer = {
            selectedOptions: response.selectedOptions,
            options: node.data.options,
          };
          break;
        case "TEXT_QUESTION":
          formattedResponse.answer = {
            text: response.answer || response.value || "",
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
      Alert.alert("Error", "No se pudo procesar la respuesta");
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

    const statusColors = {
      green: theme.colors.success,
      yellow: theme.colors.warning,
      red: theme.colors.error,
    };

    return (
      <View style={styles.reviewContainer}>
        <Text
          style={[
            styles.statusText,
            { color: statusColors[selectedCategory.status_color] },
          ]}
        >
          {selectedCategory.status_color === "green" && "✅ Estado Saludable"}
          {selectedCategory.status_color === "yellow" && "⚠️ Requiere Atención"}
          {selectedCategory.status_color === "red" && "🚨 Atención Urgente"}
        </Text>
        {selectedCategory.doctor_recommendations && (
          <View style={styles.recommendationsContainer}>
            <Text style={styles.recommendationsTitle}>
              Recomendaciones del Doctor:
            </Text>
            <Text style={styles.recommendationsText}>
              {selectedCategory.doctor_recommendations}
            </Text>
          </View>
        )}
      </View>
    );
  };

  const renderResponsesList = () => {
    if (!selectedCategory?.responses) return null;
    if (!selectedCategory?.evaluation_form?.question_nodes) {
      console.log("No hay question_nodes disponibles:", selectedCategory);
      return null;
    }

    const formatResponse = (response: any, node: QuestionNode) => {
      switch (node.type) {
        case "SINGLE_CHOICE_QUESTION":
          if (response.selectedOption !== undefined && node.data?.options) {
            return node.data.options[response.selectedOption];
          }
          break;
        case "MULTIPLE_CHOICE_QUESTION":
          if (response.selectedOptions && node.data?.options) {
            return response.selectedOptions
              .map((index: number) => node.data.options?.[index] || "")
              .join(", ");
          }
          break;
        case "TEXT_QUESTION":
          return response.answer || response.value;
      }
      return "Sin respuesta";
    };

    return (
      <View style={styles.responsesList}>
        {selectedCategory.evaluation_form.question_nodes.map((node, index) => {
          const response = selectedCategory.responses
            ? selectedCategory.responses[node.id]
            : undefined;
          return (
            <View key={node.id} style={styles.responseItem}>
              <Text style={styles.questionText}>
                {index + 1}. {node?.data?.question}
              </Text>
              <Text style={styles.answerText}>
                {response ? formatResponse(response, node) : "Sin respuesta"}
              </Text>
            </View>
          );
        })}
      </View>
    );
  };

  const renderCompletionActions = () => {
    if (!selectedCategory?.evaluation_form?.question_nodes?.length) {
      return (
        <View style={styles.completedContainer}>
          <Text style={styles.completedText}>No hay evaluación disponible</Text>
          <Text style={styles.infoText}>
            Esta categoría no tiene preguntas configuradas
          </Text>
        </View>
      );
    }

    const status = getCategoryStatus(selectedCategory);

    if (selectedCategory?.doctor_recommendations) {
      return (
        <View style={styles.completedContainer}>
          <Text style={styles.completedText}>
            {status?.text || "✅ Evaluación Completada"}
          </Text>
          <Text style={styles.infoText}>
            El doctor ha revisado tus respuestas
          </Text>
          {renderDoctorReview()}
          {renderResponsesList()}
          <TouchableOpacity
            style={[styles.startButton, { marginTop: 24 }]}
            onPress={() => {
              setEvaluationState((prev) => ({
                ...prev,
                completed: false,
                responses: [],
                currentNodeId:
                  selectedCategory?.evaluation_form?.question_nodes[0]?.id ||
                  null,
              }));
            }}
          >
            <Text style={styles.startButtonText}>
              Realizar Nueva Evaluación
            </Text>
          </TouchableOpacity>
        </View>
      );
    }

    if (status?.status === "completed" || evaluationState.completed) {
      return (
        <View style={styles.completedContainer}>
          <Text style={styles.completedText}>
            {status?.text || "✅ Evaluación Completada"}
          </Text>
          <Text style={styles.infoText}>
            Por favor, espera a que el doctor revise tus respuestas
          </Text>
          {renderResponsesList()}
        </View>
      );
    }

    return (
      <View style={styles.completedContainer}>
        <Text style={styles.completedText}>
          {status?.text || "Estado desconocido"}
        </Text>
        {status?.status === "in_progress" && (
          <Text style={styles.infoText}>Continúa donde lo dejaste</Text>
        )}
        <TouchableOpacity
          style={styles.startButton}
          onPress={() => {
            setEvaluationState((prev) => ({
              ...prev,
              completed: false,
              currentNodeId:
                selectedCategory?.evaluation_form?.question_nodes[0]?.id ||
                null,
            }));
          }}
        >
          <Text style={styles.startButtonText}>
            {status?.status === "in_progress"
              ? "Continuar Evaluación"
              : "Comenzar Evaluación"}
          </Text>
        </TouchableOpacity>
      </View>
    );
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <Text>Cargando...</Text>
      </View>
    );
  }

  if (!selectedCategory) {
    return (
      <View style={styles.container}>
        <Text style={styles.buttonText}>
          Selecciona una categoría para comenzar
        </Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {selectedCategory && <CategoryHeader name={selectedCategory.name} />}

      {evaluationState.completed
        ? renderCompletionActions()
        : renderNode(evaluationState.currentNodeId, () => {
            if (evaluationState.history.length > 0) {
              const previousNodes = [...evaluationState.history];
              const previousNodeId = previousNodes.pop();
              setEvaluationState((prev) => ({
                ...prev,
                currentNodeId: previousNodeId || null,
                history: previousNodes,
              }));
            }
          })}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  descriptionContainer: {
    backgroundColor: theme.colors.card,
    borderRadius: 12,
    padding: 20,
    marginBottom: 24,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  descriptionText: {
    fontSize: 16,
    color: theme.colors.text,
    lineHeight: 24,
  },
  completedContainer: {
    alignItems: "center",
    padding: 24,
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
    backgroundColor: theme.colors.card,
    borderRadius: 12,
    padding: 20,
    marginTop: 24,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  responseItem: {
    marginBottom: 20,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
    paddingBottom: 16,
  },
  questionText: {
    fontSize: 16,
    fontWeight: "600",
    color: theme.colors.text,
    marginBottom: 8,
  },
  answerText: {
    fontSize: 15,
    color: theme.colors.text,
    marginLeft: 16,
    lineHeight: 22,
  },
  startButton: {
    backgroundColor: theme.colors.primary,
    padding: 16,
    borderRadius: 8,
    width: "100%",
    alignItems: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  startButtonText: {
    color: theme.colors.text,
    fontSize: 18,
    fontWeight: "600",
  },
  reviewContainer: {
    padding: 16,
    backgroundColor: theme.colors.card,
    borderRadius: 8,
    marginVertical: 16,
  },
  statusText: {
    fontSize: 18,
    fontWeight: "600",
    textAlign: "center",
    marginBottom: 8,
  },
  recommendationsContainer: {
    marginTop: 16,
  },
  recommendationsTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: theme.colors.text,
    marginBottom: 8,
  },
  recommendationsText: {
    fontSize: 16,
    color: theme.colors.text,
    lineHeight: 24,
  },
  actionButton: {
    backgroundColor: theme.colors.primary,
    padding: 16,
    borderRadius: 8,
    marginTop: 16,
  },
  actionButtonText: {
    color: theme.colors.text,
    fontSize: 16,
    fontWeight: "600",
    textAlign: "center",
  },
  viewButton: {
    backgroundColor: theme.colors.primary,
  },
  buttonText: {
    color: theme.colors.text,
    fontSize: 16,
    fontWeight: "600",
  },
});

export default EvaluateScreen;
