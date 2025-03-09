
import { View, Text, StyleSheet } from "react-native";
import { theme } from "@/src/theme";

interface CategoryHeaderProps {
  name: string;
}

export const CategoryHeader = ({ name }: CategoryHeaderProps) => {
  return (
    <View style={styles.header}>
      <Text style={styles.label}>Categoría seleccionada</Text>
      <Text style={styles.title}>{name}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  header: {
    backgroundColor: theme.colors.card,
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginBottom: 4,
    textAlign: "center",
  },
  title: {
    fontSize: 18,
    fontWeight: "600",
    color: theme.colors.text,
    textAlign: "center",
  },
});
