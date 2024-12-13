import { StyleSheet } from "react-native";
import { theme } from "@/src/theme";

export const commonStyles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
    padding: 16,
  },
  question: {
    fontSize: 18,
    color: theme.colors.text,
    marginBottom: 16,
  },
  option: {
    backgroundColor: theme.colors.surface,
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: theme.colors.border,
    marginBottom: 12,
  },
  optionText: {
    fontSize: 16,
    color: theme.colors.text,
  },
  selectedOption: {
    backgroundColor: theme.colors.primary + "20",
    borderColor: theme.colors.primary,
  },
  button: {
    backgroundColor: theme.colors.primary,
    padding: 16,
    borderRadius: 8,
    alignItems: "center",
    marginTop: 16,
  },
  buttonText: {
    fontSize: 16,
    color: theme.colors.text,
    fontWeight: "600",
  },
  input: {
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: 8,
    padding: 12,
    color: theme.colors.text,
    backgroundColor: theme.colors.surface,
  },
}); 