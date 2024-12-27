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
import { Category, TrainingNode } from "@/app/types/category";

import apiService from "../services/apiService";
import { getCategoryStatus } from "@/utils/categoryHelpers";
import { CategoryHeader } from "@/components/CategoryHeader";

import ActivityNodeContainer from "@/components/ActivityNodes/ActivityNodeContainer";
import { ActivityNodeType } from "@/components/ActivityNodes";
import { useRouter } from "expo-router";
import EmptyState from "../containers/EmptyState";
import Ionicons from "react-native-vector-icons/Ionicons";

interface NodeResponse {
  nodeId: number;
  response: any;
}

interface TrainingState {
  currentNodeId: number | null;

  history: number[];
  trainingResult: {
    initial_node_id: number | null;
    nodes: TrainingNode[];
  };
}

const TrainingScreen = () => {
  const { selectedCategory, fetchCategories, updateCategory } = useCategories();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);

  useEffect(() => {
    fetchCategories();
  }, []);

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
    if (selectedCategory) {
      const status = getCategoryStatus(selectedCategory);
      const nodes = selectedCategory.training_form?.training_nodes || [];
      const existingResponses = selectedCategory.responses || {};

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

  const getNextNodeId = (currentNodeId: number): number | null => {
    if (!selectedCategory?.training_form?.training_nodes) {
      return null;
    }

    const nodes = selectedCategory.training_form.training_nodes;
    const currentIndex = nodes.findIndex((node) => node.id === currentNodeId);

    if (currentIndex === -1 || currentIndex === nodes.length - 1) {
      setIsCompleted(true); // Set completed when we reach the last node
      return null;
    }

    return nodes[currentIndex + 1].id;
  };

  const handleRestart = () => {
    const nodes = selectedCategory?.training_form?.training_nodes || [];
    setIsCompleted(false);
    setTrainingState({
      currentNodeId: nodes[0]?.id || null,
      history: [],
      trainingResult: {
        initial_node_id: nodes[0]?.id || null,
        nodes: nodes,
      },
    });
  };

  const getCurrentNode = (nodeId: number | null): TrainingNode | null => {
    if (!nodeId || !selectedCategory?.training_form?.training_nodes) {
      return null;
    }

    return (
      selectedCategory.training_form.training_nodes.find(
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
        onNext={() => {
          const nextNodeId = getNextNodeId(node.id);
          setTrainingState((prev) => ({
            ...prev,
            currentNodeId: nextNodeId || null,
            history: [...prev.history, node.id],
          }));
        }}
        onBack={() => {
          if (trainingState.history.length > 0) {
            const previousNodes = [...trainingState.history];
            const previousNodeId = previousNodes.pop();
            setTrainingState((prev) => ({
              ...prev,
              currentNodeId: previousNodeId || null,
              history: previousNodes,
            }));
          }
        }}
        categoryId={selectedCategory?.id}
        responses={[]}
      />
    );
  };

  const handleSaveResponses = async () => {
    try {
      setLoading(true);
      const result = await apiService.categories.saveResponses(
        selectedCategory.id,
        responses
      );

      // Actualizar el estado global de las categorías
      updateCategory(result.data);

      // Marcar como completado si es necesario
      setIsCompleted(true);
    } catch (error) {
      console.error("Error saving responses:", error);
      Alert.alert("Error", "No se pudieron guardar las respuestas");
    } finally {
      setLoading(false);
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
    return <EmptyState view="training" />;
  }

  return (
    <ScrollView style={styles.container}>
      {selectedCategory && <CategoryHeader name={selectedCategory.name} />}

      {isCompleted ? (
        <View style={styles.completedContainer}>
          <View style={styles.completedContent}>
            <View style={styles.iconContainer}>
              <Ionicons name="checkmark-circle" size={80} color="#4CAF50" />
            </View>
            <Text style={styles.completedTitle}>
              ¡Entrenamiento Completado!
            </Text>
            <Text style={styles.completedText}>
              Has completado el entrenamiento de esta categoría. ¿Deseas
              realizarlo nuevamente?
            </Text>
            <TouchableOpacity
              style={styles.restartButton}
              onPress={handleRestart}
            >
              <Ionicons
                name="refresh"
                size={24}
                color="white"
                style={styles.buttonIcon}
              />
              <Text style={styles.restartButtonText}>Realizar nuevamente</Text>
            </TouchableOpacity>
          </View>
        </View>
      ) : (
        renderNode(trainingState.currentNodeId, () => {
          if (trainingState.history.length > 0) {
            const previousNodes = [...trainingState.history];
            const previousNodeId = previousNodes.pop();
            setTrainingState((prev) => ({
              ...prev,
              currentNodeId: previousNodeId || null,
              history: previousNodes,
            }));
          }
        })
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  completedContainer: {
    flex: 1,
    backgroundColor: "#fff",
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
  },
  completedContent: {
    width: "100%",
    maxWidth: 400,
    backgroundColor: "#fff",
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
    elevation: 5,
  },
  iconContainer: {
    marginBottom: 20,
    padding: 16,
    borderRadius: 50,
    backgroundColor: "rgba(76, 175, 80, 0.1)",
  },
  completedTitle: {
    fontSize: 24,
    fontWeight: "700",
    color: "#2E3A59",
    textAlign: "center",
    marginBottom: 16,
  },
  completedText: {
    fontSize: 16,
    color: "#6B7280",
    textAlign: "center",
    marginBottom: 32,
    lineHeight: 24,
  },
  restartButton: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#4CAF50",
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 12,
    width: "100%",
    justifyContent: "center",
    shadowColor: "#4CAF50",
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 4,
  },
  restartButtonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  descriptionText: {
    fontSize: 16,
    color: theme.colors.text,
    lineHeight: 24,
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
  emptyStateContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: theme.spacing.xl,
  },
  emptyStateTitle: {
    marginBottom: theme.spacing.md,
    textAlign: "center",
  },
  emptyStateText: {
    textAlign: "center",
    marginBottom: theme.spacing.xl,
    color: theme.colors.textSecondary,
  },
  buttonIcon: {
    marginRight: 8,
  },
});

export default TrainingScreen;
