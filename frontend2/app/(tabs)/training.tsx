import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
} from "react-native";
import { useCategories } from "../contexts/categories";
import { theme } from "@/src/theme";
import { CategoryHeader } from "@/components/CategoryHeader";
import { WeeklyRecipeNodeView } from "@/components/ActivityNodes/views/WeeklyRecipeNodeView";

interface TrainingState {
  currentNodeIndex: number;
  responses: { [key: number]: any };
  history: number[];
  completed: boolean;
}

const TrainingScreen = () => {
  const { selectedCategory } = useCategories();
  const [trainingState, setTrainingState] = useState<TrainingState>({
    currentNodeIndex: 0,
    responses: {},
    history: [],
    completed: false,
  });

  const trainingNodes = selectedCategory?.training_nodes || [];

  useEffect(() => {
    console.log("Training nodes loaded:", trainingNodes);
  }, [trainingNodes]);

  const handleNodeResponse = (response: any) => {
    const currentNodeIndex = trainingState.currentNodeIndex;

    // Guardar la respuesta y avanzar
    const nextIndex =
      currentNodeIndex < trainingNodes.length - 1 ? currentNodeIndex + 1 : null;

    setTrainingState((prev) => ({
      ...prev,
      responses: { ...prev.responses, [currentNodeIndex]: response },
      history: [...prev.history, currentNodeIndex],
      currentNodeIndex: nextIndex !== null ? nextIndex : currentNodeIndex,
      completed: nextIndex === null,
    }));
  };

  const handleBack = () => {
    const previousHistory = [...trainingState.history];
    const lastNodeIndex = previousHistory.pop();

    if (lastNodeIndex !== undefined) {
      setTrainingState((prev) => ({
        ...prev,
        currentNodeIndex: lastNodeIndex,
        history: previousHistory,
      }));
    }
  };

  const renderMediaContent = (node: any) => {
    if (!node.media_url) return null;

    return (
      <Image
        source={{ uri: node.media_url }}
        style={styles.media}
        resizeMode="contain"
      />
    );
  };

  const renderNode = (node: any) => {
    if (!node) return null;
    const navigationButtons = (
      <View style={styles.navigationButtons}>
        {trainingState.history.length > 0 && (
          <TouchableOpacity
            style={[styles.button, styles.backButton]}
            onPress={handleBack}
          >
            <Text style={[styles.buttonText, styles.backButtonText]}>
              Anterior
            </Text>
          </TouchableOpacity>
        )}
        <TouchableOpacity
          style={[styles.button, styles.nextButton]}
          onPress={() => handleNodeResponse("completed")}
        >
          <Text style={[styles.buttonText, styles.nextButtonText]}>
            {trainingState.currentNodeIndex < trainingNodes.length - 1
              ? "Siguiente"
              : "Completar"}
          </Text>
        </TouchableOpacity>
      </View>
    );

    if (node.type === "WEEKLY_RECIPE_NODE") {
      return (
        <View style={styles.fullNodeContainer}>
          <WeeklyRecipeNodeView
            data={node}
            onNext={() => handleNodeResponse("completed")}
          />
          {navigationButtons}
        </View>
      );
    }

    return (
      <View style={styles.nodeContainer}>
        <View style={styles.contentContainer}>
          <View style={styles.headerSection}>
            <Text style={styles.title}>{node.title}</Text>
            <View style={styles.divider} />
          </View>

          {renderMediaContent(node)}

          <View style={styles.descriptionContainer}>
            <Text style={styles.description}>{node.description}</Text>
          </View>
        </View>
        {navigationButtons}
      </View>
    );
  };

  if (!selectedCategory) {
    return (
      <View style={styles.container}>
        <Text style={styles.message}>
          Selecciona una categoría para comenzar el entrenamiento
        </Text>
      </View>
    );
  }

  if (!trainingNodes.length) {
    return (
      <View style={styles.container}>
        <Text style={styles.message}>
          No hay contenido de entrenamiento disponible
        </Text>
      </View>
    );
  }

  if (trainingState.completed) {
    return (
      <View style={styles.container}>
        <Text style={styles.completedText}>
          ¡Has completado el entrenamiento!
        </Text>
        <TouchableOpacity
          style={styles.button}
          onPress={() =>
            setTrainingState({
              currentNodeIndex: 0,
              responses: {},
              history: [],
              completed: false,
            })
          }
        >
          <Text style={styles.buttonText}>Volver a Empezar</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {selectedCategory && <CategoryHeader name={selectedCategory.name} />}
      <Text style={styles.progressText}>
        Progreso: {trainingState.currentNodeIndex + 1} / {trainingNodes.length}
      </Text>
      {trainingNodes &&
        renderNode(trainingNodes[trainingState.currentNodeIndex])}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  mainContainer: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  contentContainer: {
    flex: 1,
    padding: 20,
  },
  headerSection: {
    marginBottom: 24,
  },
  divider: {
    height: 2,
    backgroundColor: theme.colors.primary,
    width: 40,
    marginTop: 8,
  },
  fullNodeContainer: {
    flex: 1,
    backgroundColor: theme.colors.card,
  },
  nodeContainer: {
    flex: 1,
    backgroundColor: theme.colors.card,
    borderRadius: 16,
    margin: 16,
    overflow: "hidden",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  title: {
    fontSize: 24,
    fontWeight: "800",
    color: theme.colors.text,
    letterSpacing: 0.5,
  },
  descriptionContainer: {
    backgroundColor: theme.colors.background,
    padding: 16,
    borderRadius: 12,
    marginTop: 16,
  },
  description: {
    fontSize: 16,
    color: theme.colors.text,
    lineHeight: 24,
    letterSpacing: 0.3,
  },
  media: {
    width: "100%",
    height: 200,
    borderRadius: 12,
    marginBottom: 20,
  },
  navigationButtons: {
    flexDirection: "row",
    justifyContent: "space-between",
    padding: 16,
    gap: 12,
    backgroundColor: theme.colors.card,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
  },
  button: {
    flex: 1,
    padding: 16,
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center",
  },
  backButton: {
    backgroundColor: theme.colors.background,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  nextButton: {
    backgroundColor: theme.colors.primary,
  },
  buttonText: {
    fontSize: 16,
    fontWeight: "600",
  },
  backButtonText: {
    color: theme.colors.text,
  },
  nextButtonText: {
    color: theme.colors.white,
  },
  progressText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    textAlign: "center",
    marginVertical: 16,
    fontWeight: "500",
  },
  completedText: {
    fontSize: 24,
    fontWeight: "700",
    color: theme.colors.success,
    textAlign: "center",
    marginBottom: 32,
  },
});

export default TrainingScreen;
