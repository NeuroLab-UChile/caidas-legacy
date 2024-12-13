// frontend2/app/(tabs)/evaluate.tsx
import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
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
}

const EvaluateScreen = () => {
  const { selectedCategory } = useCategories();

  if (!selectedCategory?.evaluation_form?.question_nodes?.length) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>
          Esta categoría no tiene preguntas disponibles
        </Text>
      </View>
    );
  }

  const [evaluationState, setEvaluationState] = useState<EvaluationState>(
    () => {
      const firstNode = selectedCategory.evaluation_form.question_nodes[0];
      return {
        currentNodeId: firstNode.id,
        responses: {},
        completed: false,
        history: [],
      };
    }
  );

  const handleBack = () => {
    if (evaluationState.history.length > 0) {
      const previousNodes = [...evaluationState.history];
      const previousNodeId = previousNodes.pop();

      setEvaluationState((prev) => ({
        ...prev,
        currentNodeId: previousNodeId || null,
        history: previousNodes,
      }));
    }
  };

  const handleNodeResponse = (
    nodeId: number,
    response: any,
    nextNodeId: number | null
  ) => {
    setEvaluationState((prev) => ({
      ...prev,
      responses: {
        ...prev.responses,
        [nodeId]: response,
      },
      currentNodeId: nextNodeId,
      completed: !nextNodeId,
      history: [...prev.history, nodeId],
    }));
  };

  const submitEvaluation = async () => {
    try {
      const response = await apiService.request(
        `/health-categories/${selectedCategory?.id}/responses`,
        {
          method: "POST",
          body: JSON.stringify({
            responses: evaluationState.responses,
          }),
        }
      );

      if (response.status === 200) {
        setEvaluationState({
          currentNodeId: null,
          responses: {},
          completed: true,
          history: [],
        });
      }
    } catch (error) {
      console.error("Error:", error);
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
        onNext={(response) =>
          handleNodeResponse(node.id, response, node.next_node_id || null)
        }
        onBack={handleBack}
        categoryId={selectedCategory?.id}
        responses={evaluationState.responses}
      />
    );
  };

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
      {evaluationState.completed ? (
        <View style={styles.completedContainer}>
          <Text style={styles.completedText}>
            ¡Evaluación lista para revisar!
          </Text>
          <TouchableOpacity
            style={styles.submitButton}
            onPress={submitEvaluation}
          >
            <Text style={styles.submitButtonText}>Evaluar Respuestas</Text>
          </TouchableOpacity>
        </View>
      ) : (
        renderNode(evaluationState.currentNodeId, handleBack)
      )}
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
});

export default EvaluateScreen;
