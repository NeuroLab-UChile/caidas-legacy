import { StyleSheet } from "react-native";
import { theme } from "@/src/theme";

export const commonStyles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: theme.colors.background,
  },
  text: {
    fontSize: 17,
    color: "#000",
    marginBottom: 16,
  },
  input: {
    height: 56,
    borderRadius: 16,
    padding: 16,
    backgroundColor: theme.colors.background,
    borderWidth: 1,
    borderColor: theme.colors.border,
    color: "#000",
  },
  btn: {
    height: 56,
    borderRadius: 16,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: theme.colors.primary,
    borderWidth: 1,
    borderColor: "#000",
  },
  btnText: {
    fontSize: 17,
    color: "#000",
    fontWeight: "600",
  },
  btnOutline: {
    backgroundColor: "transparent",
    borderWidth: 1,
    borderColor: theme.colors.primary,
  },
  btnDisabled: {
    backgroundColor: theme.colors.disabled,
    borderColor: "transparent",
  },
  row: {
    flexDirection: "row",
    gap: 12,
  },
}); 