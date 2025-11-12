import React from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { theme } from "@/src/theme";

interface NavigationBarProps {
  onBack?: () => void;
  onNext?: () => void;
  nextDisabled?: boolean;
  currentStep?: number;
  totalSteps?: number;
  nextText?: string;
  backText?: string;
  type?: "training" | "evaluation";
}

export const NavigationBar: React.FC<NavigationBarProps> = ({
  onBack,
  onNext,
  nextDisabled = false,
  currentStep,
  totalSteps,
  nextText = "Siguiente",
  backText = "Volver",
  type = "training",
}) => {
  return (
    <View style={styles.container}>
      {/* Header con botón de volver y progreso */}
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={onBack}>
          <Ionicons
            name="chevron-back"
            size={theme.typography.sizes.headline1}
            color={theme.colors.text}
          />
          <Text style={styles.backButtonText}>{backText}</Text>
        </TouchableOpacity>

        {currentStep !== undefined && totalSteps !== undefined && (
          <Text style={styles.progressText}>
            Paso {currentStep} de {totalSteps}
          </Text>
        )}
      </View>

      {/* Botón de siguiente */}
      {onNext && (
        <TouchableOpacity
          style={[
            styles.nextButton,
            nextDisabled ? styles.nextButtonDisabled : styles.nextButtonEnabled,
          ]}
          onPress={onNext}
          disabled={nextDisabled}
        >
          <Text
            style={[
              styles.nextButtonText,
              nextDisabled
                ? styles.nextButtonTextDisabled
                : styles.nextButtonTextEnabled,
            ]}
          >
            {nextText}
          </Text>
          <Ionicons
            name="chevron-forward"
            size={theme.typography.sizes.headline1}
            color={
              nextDisabled
                ? theme.colors.textSecondary
                : theme.colors.background
            }
          />
        </TouchableOpacity>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 16,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: theme.typography.sizes.body2,
  },
  backButton: {
    flexDirection: "row",
    alignItems: "center",
    padding: 8,
  },
  backButtonText: {
    marginLeft: 4,
    fontSize: theme.typography.sizes.body1,
    color: theme.colors.text,
    fontWeight: "600",
  },
  progressText: {
    fontSize: theme.typography.sizes.body2,
    color: theme.colors.textSecondary,
  },
  nextButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    padding: 16,
    borderRadius: 12,
    marginTop: 16,
  },
  nextButtonEnabled: {
    backgroundColor: theme.colors.primary,
    opacity: 1,
  },
  nextButtonDisabled: {
    backgroundColor: `${theme.colors.primary}15`,
    opacity: 0.7,
  },
  nextButtonText: {
    fontSize: theme.typography.sizes.body1,
    fontWeight: "600",
    marginRight: 8,
  },
  nextButtonTextEnabled: {
    color: theme.colors.background,
  },
  nextButtonTextDisabled: {
    color: theme.colors.textSecondary,
  },
});
