// frontend2/app/(tabs)/TrainScreen.tsx
import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { useCategories } from "../contexts/categories";
import { theme } from "@/src/theme";

const TrainScreen = () => {
  const { selectedCategory } = useCategories();

  return (
    <View style={styles.container}>
      <Text style={styles.text}>
        {selectedCategory
          ? `Categoría seleccionada: ${selectedCategory.name}`
          : "No hay categoría seleccionada"}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 16,
  },
  text: {
    fontSize: 18,
    color: theme.colors.text,
    textAlign: "center",
  },
});

export default TrainScreen;
