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
  ScrollView,
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

  const renderIcon = (base64Icon: string) => {
    try {
      console.log("Base64 icon:", base64Icon);
      // Validar que tenemos un string no vacío
      if (!base64Icon || typeof base64Icon !== "string") {
        console.log("Invalid icon data:", base64Icon);
        return null;
      }

      // Limpiar el string base64 de posibles espacios o saltos de línea
      const cleanBase64 = base64Icon.trim();

      // Debug logs detallados
      console.log("Icon processing:", {
        originalLength: base64Icon.length,
        cleanedLength: cleanBase64.length,
        startsWithData: cleanBase64.startsWith("data:"),
        startsWithSlash: cleanBase64.startsWith("/"),
        first50Chars: cleanBase64.substring(0, 50),
      });

      // Construir URI según el formato
      let imageUri = cleanBase64;
      if (!cleanBase64.startsWith("data:") && !cleanBase64.startsWith("http")) {
        // Si no empieza con data: o http, asumimos que es base64 puro
        imageUri = `data:image/png;base64,${cleanBase64}`;
      }

      console.log(
        "Final image URI (first 100 chars):",
        imageUri.substring(0, 100)
      );

      return (
        <Image
          source={{ uri: imageUri }}
          style={styles.iconImage}
          resizeMode="contain"
          onError={(e) => {
            console.error("Image loading error:", {
              error: e.nativeEvent.error,
              uri: imageUri.substring(0, 100) + "...",
            });
          }}
          onLoad={() => console.log("Image loaded successfully")}
        />
      );
    } catch (error) {
      console.error("Error in renderIcon:", error);
      return null;
    }
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
        ListHeaderComponent={null}
        showsVerticalScrollIndicator={true}
        bounces={true}
        renderItem={({ item }) => {
          console.log("Rendering category:", {
            id: item.id,
            name: item.name,
            hasIcon: !!item.icon,
            iconLength: item.icon?.length,
          });

          return (
            <TouchableOpacity
              style={[
                styles.categoryCard,
                selectedCategory?.id === item.id && styles.selectedCard,
                { backgroundColor: theme.colors.background },
              ]}
              onPress={() => handleCategoryPress(item)}
            >
              <View style={styles.iconContainer}>
                {item.icon ? (
                  renderIcon(item.icon)
                ) : (
                  <Text style={styles.categoryName}>No Icon</Text>
                )}
              </View>
              <Text style={[styles.categoryName, { color: theme.colors.text }]}>
                {item.name}
              </Text>
            </TouchableOpacity>
          );
        }}
        keyExtractor={(item) => item.id.toString()}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  contentContainer: {
    flexGrow: 1,
    paddingBottom: 100, // Espacio extra al final para el scroll
  },
  content: {
    padding: 16,
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
