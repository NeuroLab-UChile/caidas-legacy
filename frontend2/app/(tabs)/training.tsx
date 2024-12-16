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

  const renderNode = (node: any) => (
    <View style={styles.nodeContainer}>
      <Text style={styles.title}>{node.title}</Text>
      {renderMediaContent(node)}
      <Text style={styles.description}>{node.description}</Text>

      <View style={styles.navigationButtons}>
        {trainingState.history.length > 0 && (
          <TouchableOpacity
            style={[styles.button, styles.backButton]}
            onPress={handleBack}
          >
            <Text style={styles.buttonText}>Anterior</Text>
          </TouchableOpacity>
        )}
        <TouchableOpacity
          style={[styles.button, styles.nextButton]}
          onPress={() => handleNodeResponse("completed")}
        >
          <Text style={styles.buttonText}>
            {trainingState.currentNodeIndex < trainingNodes.length - 1
              ? "Siguiente"
              : "Completar"}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );

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
      <Text style={styles.progressText}>
        Progreso: {trainingState.currentNodeIndex + 1} / {trainingNodes.length}
      </Text>
      {renderNode(trainingNodes[trainingState.currentNodeIndex])}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  nodeContainer: {
    backgroundColor: theme.colors.card,
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: "600",
    color: theme.colors.text,
    marginBottom: 16,
  },
  description: {
    fontSize: 16,
    color: theme.colors.text,
    marginBottom: 16,
    lineHeight: 24,
  },
  media: {
    width: "100%",
    height: 200,
    marginBottom: 16,
    borderRadius: 8,
  },
  navigationButtons: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginTop: 16,
  },
  button: {
    padding: 12,
    borderRadius: 8,
    minWidth: 100,
    alignItems: "center",
  },
  backButton: {
    backgroundColor: theme.colors.card,
  },
  nextButton: {
    backgroundColor: theme.colors.primary,
  },
  buttonText: {
    color: theme.colors.text,
    fontSize: 16,
    fontWeight: "600",
  },
  message: {
    fontSize: 18,
    color: theme.colors.text,
    textAlign: "center",
  },
  completedText: {
    fontSize: 24,
    color: theme.colors.success,
    textAlign: "center",
    marginBottom: 24,
  },
  progressText: {
    fontSize: 18,
    color: theme.colors.text,
    marginBottom: 16,
    textAlign: "center",
  },
});

export default TrainingScreen;
