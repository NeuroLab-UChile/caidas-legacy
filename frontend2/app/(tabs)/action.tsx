// frontend2/app/(tabs)/ActionScreen.tsx
import React from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  Dimensions,
  Image,
} from "react-native";
import { useCategories } from "../contexts/categories";
import { theme } from "@/src/theme";
import { Category } from "../types/category";
import { router } from "expo-router";

const { width } = Dimensions.get("window");
const COLUMN_COUNT = 2;
const SPACING = 16;
const ITEM_WIDTH = (width - SPACING * (COLUMN_COUNT + 1)) / COLUMN_COUNT;

export default function ActionScreen() {
  const { categories, selectedCategory, setSelectedCategory, loading, error } =
    useCategories();

  const handleCategoryPress = (category: Category) => {
    setSelectedCategory(category);
    router.push({
      pathname: "/(tabs)/category-detail",
    });
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>{error}</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.selectedCategoryContainer}>
        <Text style={styles.selectedCategoryTitle}>
          {selectedCategory
            ? `Categoría seleccionada: ${selectedCategory.name}`
            : "No hay categoría seleccionada"}
        </Text>
      </View>

      <FlatList
        data={categories}
        numColumns={COLUMN_COUNT}
        contentContainerStyle={styles.listContainer}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={[
              styles.categoryCard,
              selectedCategory?.id === item.id && styles.selectedCard,
              { backgroundColor: theme.colors.background },
            ]}
            onPress={() => handleCategoryPress(item)}
          >
            <View style={styles.iconContainer}>
              {item.icon && (
                <Image
                  source={{ uri: `data:image/png;base64,${item.icon}` }}
                  style={styles.iconImage}
                  resizeMode="contain"
                />
              )}
            </View>
            <Text style={[styles.categoryName, { color: theme.colors.text }]}>
              {item.name}
            </Text>
          </TouchableOpacity>
        )}
        keyExtractor={(item) => item.id.toString()}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: SPACING,
  },
  selectedCategoryContainer: {
    padding: SPACING,
    marginBottom: SPACING,
    backgroundColor: theme.colors.background,
    borderRadius: 8,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  selectedCategoryTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: theme.colors.text,
    textAlign: "center",
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  errorContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
  },
  errorText: {
    color: theme.colors.text,
    textAlign: "center",
  },
  listContainer: {
    paddingBottom: SPACING,
  },
  categoryCard: {
    width: ITEM_WIDTH,
    margin: SPACING / 2,
    padding: SPACING,
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  selectedCard: {
    borderWidth: 2,
    borderColor: theme.colors.primary,
  },
  iconContainer: {
    width: 80,
    height: 80,
    justifyContent: "center",
    alignItems: "center",
  },
  iconImage: {
    width: "100%",
    height: "100%",
  },
  categoryName: {
    marginTop: 8,
    fontSize: 16,
    fontWeight: "600",
    textAlign: "center",
  },
});
