import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  SafeAreaView,
  Platform,
  Image,
  KeyboardAvoidingView,
  Alert,
  Modal,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { theme } from "@/src/theme";
import { ActivityNodeViews, ActivityNodeType } from "./index";
import { ResultNodeView } from "./views/ResultNodeView";
import { VideoNodeView } from "./views/VideoNodeView";
import { ImageNodeView } from "./views/ImageNode";
import { router } from 'expo-router';
import { StepIndicator } from '../ui/StepIndicator';
import { NavigationBar } from '../ui/NavigationBar';
import { TextNodeView } from './views/TextNodeView';
import { SingleChoiceQuestionView } from './views/SingleChoiceQuestionView';
import { MultipleChoiceQuestionView } from './views/MultipleChoiceQuestionView';
import { TextQuestionView } from './views/TextQuestionView';
import { ScaleQuestionView } from './views/ScaleQuestionView';
import { ImageQuestionView } from './views/ImageQuestionView';
import { WeeklyRecipeNodeView } from './views/WeeklyRecipeNodeView';
import { CategoryDescriptionView } from './views/CategoryDescriptionView';

interface ActivityNodeContainerProps {
  type: ActivityNodeType;
  data: any;
  onNext?: (response?: any) => void;
  onBack?: () => void;
  categoryId?: number;
  responses?: any[];
  history?: number[];
  setHistory?: (history: number[]) => void;
  currentQuestionIndex: number;
  totalQuestions: number;
  nodeType?: 'training' | 'evaluation';
}

export const ActivityNodeContainer: React.FC<ActivityNodeContainerProps> = ({
  type,
  data,
  onNext,
  onBack,
  categoryId,
  responses = [],
  history = [],
  setHistory,
  currentQuestionIndex,
  totalQuestions,
  nodeType = 'training'
}) => {
  const [currentResponse, setCurrentResponse] = useState<any>(null);
  const [showExitModal, setShowExitModal] = useState(false);

  const NodeComponent =
    ActivityNodeViews[type as keyof typeof ActivityNodeViews];

  const handleBack = () => {
    const message = nodeType === 'training' 
      ? '¿Deseas finalizar el entrenamiento?' 
      : '¿Deseas finalizar la evaluación?';
      
    Alert.alert(
      'Confirmar salida',
      message,
      [
        {
          text: 'Cancelar',
          style: 'cancel',
        },
        {
          text: 'Sí, finalizar',
          style: 'destructive',
          onPress: onBack
        },
      ]
    );
  };

  const handleNext = (response?: any) => {
    if (onNext) {
      onNext(response || currentResponse);
    }
  };

  const ExitConfirmationModal = () => (
    <Modal
      animationType="fade"
      transparent={true}
      visible={showExitModal}
      onRequestClose={() => setShowExitModal(false)}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          <Text style={styles.modalTitle}>Salir de la evaluación</Text>
          <Text style={styles.modalText}>
            ¿Estás seguro que deseas salir? Se perderá el progreso.
          </Text>
          <View style={styles.modalButtons}>
            <TouchableOpacity
              style={[styles.modalButton, styles.cancelButton]}
              onPress={() => setShowExitModal(false)}
            >
              <Text style={styles.cancelButtonText}>CANCELAR</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.modalButton, styles.exitButton]}
              onPress={() => {
                setShowExitModal(false);
                router.push("/(tabs)/action");
              }}
            >
              <Text style={styles.exitButtonText}>SALIR</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );

  const renderContent = () => {
    const commonProps = {
      data,
      onNext: handleNext,
      setResponse: setCurrentResponse
    };

    console.log('Rendering node type:', type);
    console.log('Node data:', data);

    switch (type) {
      case "VIDEO_NODE":
        console.log('Rendering video node with data:', data);
        return <VideoNodeView {...commonProps} />;
      case "RESULT_NODE":
        return <ResultNodeView {...commonProps} />;
      case "WEEKLY_RECIPE_NODE":
        return <WeeklyRecipeNodeView data={data} />;
      case "IMAGE_NODE":
        return <ImageNodeView {...commonProps} />;
      case "TEXT_NODE":
        return <TextNodeView data={data} />;
      case "DESCRIPTION_NODE":
        return <CategoryDescriptionView {...commonProps} />;
      case "SINGLE_CHOICE_QUESTION":
        return <SingleChoiceQuestionView {...commonProps} />;
      case "MULTIPLE_CHOICE_QUESTION":
        return <MultipleChoiceQuestionView {...commonProps} />;
      case "TEXT_QUESTION":
        return <TextQuestionView {...commonProps} />;
      case "SCALE_QUESTION":
        return <ScaleQuestionView {...commonProps} />;
      case "IMAGE_QUESTION":
        return <ImageQuestionView {...commonProps} />;
      default:
        return null;
    }
  };

  const getButtonText = () => {
    switch (type) {
      case "RESULT_NODE":
        return "Finalizar";
      case "WEEKLY_RECIPE_NODE":
        return "Continuar";
      default:
        return "Siguiente";
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        style={styles.container}
      >
        <View style={styles.header}>
          <TouchableOpacity style={styles.backButton} onPress={handleBack}>
            <Text style={styles.backText}>Volver</Text>
          </TouchableOpacity>
          <StepIndicator current={currentQuestionIndex + 1} total={totalQuestions} />
        </View>

        <ScrollView
          style={styles.content}
          contentContainerStyle={styles.contentContainer}
          showsVerticalScrollIndicator={false}
        >
          {renderContent()}
        </ScrollView>

    
          <View style={styles.buttonContainer}>
            <TouchableOpacity
              style={[
                styles.nextButton,
                (type.includes('QUESTION') && !currentResponse) && styles.nextButtonDisabled
              ]}
              onPress={handleNext}
              disabled={type.includes('QUESTION') && !currentResponse}
            >
              <Text style={styles.nextText}>{getButtonText()}</Text>
            </TouchableOpacity>
          </View>
    
      </KeyboardAvoidingView>
      <ExitConfirmationModal />
    </SafeAreaView>
  );
};

const BUTTON_HEIGHT = 70;
const BOTTOM_NAV_HEIGHT = 90;

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  backButton: {
    padding: 8,
  },
  backText: {
    fontSize: 16,
    color: theme.colors.text,
    fontWeight: '500',
  },
  content: {
    flex: 1,
  },
  contentContainer: {
    padding: 16,
    paddingBottom: 100,
  },
  buttonContainer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    paddingHorizontal: 16,
    paddingBottom: 24,
    paddingTop: 12,
    backgroundColor: theme.colors.background,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
  },
  nextButton: {
    backgroundColor: theme.colors.primary,
    borderRadius: 16,
    height: 56,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 4,
  },
  nextButtonDisabled: {
    backgroundColor: theme.colors.disabled,
    opacity: 0.7,
  },
  nextText: {
    color: theme.colors.text,
    fontSize: 18,
    fontWeight: '600',
    letterSpacing: 0.5,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modalContent: {
    backgroundColor: theme.colors.background,
    borderRadius: 16,
    padding: 24,
    width: '100%',
    maxWidth: 400,
    alignItems: 'center',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: 12,
  },
  modalText: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginBottom: 24,
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
    gap: 12,
  },
  modalButton: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  cancelButton: {
    backgroundColor: `${theme.colors.primary}15`,
  },
  exitButton: {
    backgroundColor: theme.colors.error,
  },
  cancelButtonText: {
    color: theme.colors.primary,
    fontSize: 14,
    fontWeight: '600',
  },
  exitButtonText: {
    color: theme.colors.background,
    fontSize: 14,
    fontWeight: '600',
  },
});

export default ActivityNodeContainer;
