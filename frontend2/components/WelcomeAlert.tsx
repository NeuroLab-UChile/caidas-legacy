import React from "react";
import {
  Modal,
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
} from "react-native";
import { theme } from "@/src/theme";

interface WelcomeAlertProps {
  visible: boolean;
  title: string;
  message: string;
  showOnPostpone?: boolean; // Optional prop to control the visibility of the postpone button
  eventId?: number; // Optional prop to identify the event
  onPostpone: () => void;
  onClose: () => void;
}

export const WelcomeAlert: React.FC<WelcomeAlertProps> = ({
  visible,
  title,
  message,
  showOnPostpone = false, // Default to false if not provided
  eventId = 0, // Default to 0 if not provided
  onPostpone,
  onClose,
}) => {
  if (!visible) {
    return null;
  }

  return (
    <Modal
      transparent={true}
      animationType="fade"
      visible={visible}
      onRequestClose={onClose}
    >
      <View style={styles.overlay}>
        <View style={styles.alertContainer}>
          <Text style={styles.title}>{title}</Text>

          <ScrollView style={styles.messageScrollView}>
            <Text style={styles.message}>{message}</Text>
          </ScrollView>

          {showOnPostpone && (
            <TouchableOpacity
              activeOpacity={0.8}
              style={styles.button}
              onPress={onPostpone}
            >
              <Text style={styles.buttonText}>Posponer 1 semana</Text>
            </TouchableOpacity>
          )}

          <TouchableOpacity
            activeOpacity={0.8}
            style={[styles.button, { backgroundColor: "#4AEF80" }]}
            onPress={onClose}
          >
            <Text style={styles.buttonText}>Entendido</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: "rgba(0, 0, 0, 0.6)",
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
  },
  alertContainer: {
    width: "90%",
    maxWidth: 550,
    backgroundColor: theme.colors.background,
    borderRadius: 20,
    padding: 24,
    alignItems: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 5,
  },
  title: {
    fontSize: 28,
    fontWeight: "bold",
    color: theme.colors.text,
    marginBottom: 16,
    textAlign: "center",
  },
  messageScrollView: {
    maxHeight: 350,
    width: "100%",
    marginBottom: 24,
  },
  message: {
    fontSize: 22,
    color: theme.colors.text,
    textAlign: "center",
    lineHeight: 34,
  },
  button: {
    backgroundColor: theme.colors.primary,
    borderRadius: 12,
    paddingVertical: 16,
    paddingHorizontal: 32,
    width: "100%",
    alignItems: "center",
    margin: 8,
  },
  buttonText: {
    color: theme.colors.text,
    fontSize: 20,
    fontWeight: "600",
  },
});
