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
import { ActivityNodeContainer } from "@/components/ActivityNodes/ActivityNodeContainer";
import apiService from "../services/apiService";

interface NodeResponse {
  nodeId: number;
  response: any;
}

interface EvaluationState {
  currentNodeId: number | null;
  responses: { [key: number]: any };
  completed: boolean;
  history: number[];
  evaluationResult: {
    initial_node_id: number | null;
    nodes: QuestionNode[];
  };
}

const EvaluateScreen = () => {
  const { selectedCategory } = useCategories();
  const [loading, setLoading] = useState(false);

  // Determinar si ya hay una evaluación completada y revisada por el doctor
  const hasDocterReview =
    selectedCategory?.status_color && selectedCategory?.doctor_recommendations;
  const hasCompletedEvaluation =
    selectedCategory?.responses &&
    Object.keys(selectedCategory.responses).length > 0;

  const [evaluationState, setEvaluationState] = useState<EvaluationState>(
    () => {
      if (!selectedCategory?.evaluation_form?.question_nodes) {
        return {
          currentNodeId: null,
          responses: {},
          completed: false,
          history: [],
          evaluationResult: {
            initial_node_id: null,
            nodes: [],
          },
        };
      }

      const nodes = selectedCategory.evaluation_form.question_nodes;
      return {
        currentNodeId: nodes[0]?.id || null,
        responses: selectedCategory.responses || {},
        completed: Boolean(hasCompletedEvaluation),
        history: [],
        evaluationResult: {
          initial_node_id: nodes[0]?.id || null,
          nodes: nodes,
        },
      };
    }
  );

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
      setEvaluationState((prev) => {
        const newResponses = {
          ...prev.responses,
          [nodeId]: response,
        };

        // Obtener el siguiente nodo automáticamente
        const nextNodeId = getNextNodeId(nodeId);
        const isCompleted = !nextNodeId;

        // Si está completado, guardar todas las respuestas
        if (isCompleted && selectedCategory?.id) {
          apiService.categories.saveResponses(
            selectedCategory.id,
            newResponses
          );
        }

        return {
          ...prev,
          responses: newResponses,
          currentNodeId: nextNodeId,
          completed: isCompleted,
          history: [...prev.history, nodeId],
        };
      });
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
        type={node.type}
        data={node}
        onNext={(response) => handleNodeResponse(node.id, response)}
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

    return (
      <View style={styles.responsesList}>
        {selectedCategory.evaluation_form?.question_nodes.map((node, index) => (
          <View key={node.id} style={styles.responseItem}>
            <Text style={styles.questionText}>
              {index + 1}. {node?.data?.question}
            </Text>
            <Text style={styles.answerText}>
              {selectedCategory?.responses?.[node.id]?.answer ||
                selectedCategory?.responses?.[node.id]?.selectedOption ||
                selectedCategory?.responses?.[node.id]?.value ||
                "Sin respuesta"}
            </Text>
          </View>
        ))}
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

    if (hasDocterReview) {
      return (
        <View style={styles.completedContainer}>
          <Text style={styles.completedText}>
            Ya has completado esta evaluación
          </Text>
          <Text style={styles.infoText}>
            El doctor ha revisado tus respuestas
          </Text>
          {renderDoctorReview()}
          {renderResponsesList()}
        </View>
      );
    }

    if (hasCompletedEvaluation) {
      return (
        <View style={styles.completedContainer}>
          <Text style={styles.completedText}>
            Ya has completado esta evaluación
          </Text>
          <Text style={styles.infoText}>
            Tus respuestas están pendientes de revisión por el doctor
          </Text>
          {renderResponsesList()}
        </View>
      );
    }

    return (
      <View style={styles.completedContainer}>
        <Text style={styles.completedText}>¡Has completado la evaluación!</Text>
        <TouchableOpacity
          style={styles.submitButton}
          onPress={async () => {
            try {
              if (selectedCategory?.id) {
                setLoading(true);
                await apiService.categories.saveResponses(
                  selectedCategory.id,
                  evaluationState.responses
                );
                Alert.alert("Éxito", "Evaluación guardada correctamente");
              }
            } catch (error) {
              console.error("Error saving final responses:", error);
              Alert.alert("Error", "No se pudo guardar la evaluación");
            } finally {
              setLoading(false);
            }
          }}
        >
          <Text style={styles.submitButtonText}>Guardar Evaluación</Text>
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
  nodeContainer: {
    marginBottom: 20,
  },
  description: {
    fontSize: 16,
    color: theme.colors.text,
    marginBottom: 16,
  },
  question: {
    fontSize: 18,
    fontWeight: "600",
    color: theme.colors.text,
    marginBottom: 16,
  },
  button: {
    backgroundColor: theme.colors.primary,
    padding: 12,
    borderRadius: 8,
    alignItems: "center",
  },
  buttonText: {
    color: theme.colors.text,
    fontSize: 16,
    fontWeight: "600",
  },
  optionButton: {
    backgroundColor: theme.colors.card,
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
    borderWidth: 2,
    borderColor: theme.colors.border,
  },
  optionText: {
    color: theme.colors.text,
    fontSize: 16,
  },
  completedContainer: {
    alignItems: "center",
    padding: 20,
  },
  completedText: {
    fontSize: 20,
    color: theme.colors.text,
    marginBottom: 20,
  },
  submitButton: {
    backgroundColor: theme.colors.primary,
    padding: 16,
    borderRadius: 8,
    width: "100%",
    alignItems: "center",
  },
  submitButtonText: {
    color: theme.colors.text,
    fontSize: 18,
    fontWeight: "600",
  },
  errorText: {
    fontSize: 18,
    color: theme.colors.text,
    textAlign: "center",
    marginTop: 20,
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
  infoText: {
    fontSize: 16,
    color: theme.colors.text,
    textAlign: "center",
    marginBottom: 16,
  },
  viewButton: {
    backgroundColor: theme.colors.secondary,
  },
  responsesList: {
    width: "100%",
    marginTop: 16,
    padding: 16,
    backgroundColor: theme.colors.card,
    borderRadius: 8,
  },
  responseItem: {
    marginBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
    paddingBottom: 8,
  },
  questionText: {
    fontSize: 16,
    fontWeight: "600",
    color: theme.colors.text,
    marginBottom: 4,
  },
  answerText: {
    fontSize: 14,
    color: theme.colors.text,
    marginLeft: 16,
  },
});

export default EvaluateScreen;
