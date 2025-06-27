import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Dimensions,
  Image,
  StatusBar,
  ScrollView,
} from "react-native";
import { useCategories } from "../contexts/categories";
import { theme } from "@/src/theme";
import { Category } from "../types/category";
import { router } from "expo-router";
import { IconSymbol } from "@/components/ui/IconSymbol";

const { width } = Dimensions.get("window");
const SPACING = 8; // 16;
const COLUMNS = 2;
const CARD_WIDTH = (width - SPACING * (COLUMNS + 1)) / COLUMNS;

export default function ActionScreen() {
  const { categories, selectedCategory, setSelectedCategory, loading, error } =
    useCategories();
  // const [isCategoriesExpanded, setIsCategoriesExpanded] = useState(false);
  const isCategoriesExpanded = true; // Mantener expandido por defecto

  const handleCategoryPress = (category: Category) => {
    setSelectedCategory(category);
    router.push("/(tabs)/category-detail");
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
        <TouchableOpacity
          style={styles.retryButton}
          onPress={() => {
            router.push("/(tabs)/action");
          }}
        >
          <Text style={styles.retryText}>Reintentar</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const renderIcon = (iconUrl: string | null) => {
    try {
      // Si no hay URL, mostrar icono por defecto
      if (!iconUrl) {
        return <IconSymbol name="folder" size={24} color={theme.colors.text} />;
      }

      // Validar que la URL sea string y tenga formato correcto
      if (typeof iconUrl !== "string") {
        console.warn("Invalid icon URL type:", typeof iconUrl);
        return <IconSymbol name="folder" size={24} color={theme.colors.text} />;
      }

      // Manejar URLs absolutas
      if (iconUrl.startsWith("http")) {
        return (
          <Image
            source={{ uri: iconUrl }}
            style={styles.iconImage}
            resizeMode="contain"
            defaultSource={require("@/assets/images/default-icon.png")}
            onError={(error) => {
              console.warn("Error loading image:", error.nativeEvent.error);
            }}
          />
        );
      }

      // Para URLs relativas o base64, asegurarse de que sean válidas
      if (iconUrl.startsWith("data:image/") || iconUrl.startsWith("/media/")) {
        return (
          <Image
            source={{ uri: iconUrl }}
            style={styles.iconImage}
            resizeMode="contain"
            defaultSource={require("@/assets/images/default-icon.png")}
            onError={(error) => {
              console.warn("Error loading image:", error.nativeEvent.error);
            }}
          />
        );
      }

      // Si no coincide con ningún formato válido, mostrar icono por defecto
      console.warn("Unsupported icon URL format:", iconUrl);
      return <IconSymbol name="folder" size={24} color={theme.colors.text} />;
    } catch (error) {
      console.error("Error rendering icon:", error);
      return <IconSymbol name="folder" size={24} color={theme.colors.text} />;
    }
  };

  const renderCategoryCard = (item: Category) => {
    const isSelected = selectedCategory?.id === item.id;

    return (
      <TouchableOpacity
        key={item.id}
        style={[styles.categoryCard, isSelected && styles.selectedCategoryCard]}
        onPress={() => handleCategoryPress(item)}
      >
        <View style={styles.iconContainer}>
          {item.icon ? (
            renderIcon(item.icon)
          ) : (
            <IconSymbol name="folder" size={24} color={theme.colors.text} />
          )}
        </View>
        <Text style={styles.categoryCardTitle}>{item.name || ""}</Text>
      </TouchableOpacity>
    );
  };

  const renderCategoryPair = (categories: Category[], startIndex: number) => {
    const pair = categories.slice(startIndex, startIndex + 2);
    return (
      <View key={startIndex} style={styles.categoryRow}>
        {pair.map((item) => renderCategoryCard(item))}
        {pair.length === 1 && <View style={styles.categoryCard} />}
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" />
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.mainActions}>
          <TouchableOpacity
            style={styles.actionCard}
            onPress={() => router.push("/(tabs)/events")}
          >
            <IconSymbol name="calendar" size={32} color={theme.colors.text} />
            <Text style={styles.actionTitle}>Eventos</Text>
            {/* <Text style={styles.actionSubtitle}>Ver próximos eventos</Text> */}
          </TouchableOpacity>

          {/* <TouchableOpacity
            style={styles.actionCard}
            onPress={() => setIsCategoriesExpanded(!isCategoriesExpanded)}
          >
            <IconSymbol name="folder" size={32} color={theme.colors.text} />
            <Text style={styles.actionTitle}>Categorías</Text>
            <Text style={styles.actionSubtitle}>
              Explorar o Elegir categorías
            </Text>
            <View style={styles.expandIconContainer}>
              <IconSymbol
                name="chevron-down"
                size={24}
                color={theme.colors.text}
                style={[
                  styles.expandIcon,
                  isCategoriesExpanded && styles.expandIconRotated,
                ]}
              />
            </View>
          </TouchableOpacity> */}

          <Text style={styles.actionTitle}>Categorías</Text>

          {isCategoriesExpanded && (
            <View style={styles.expandedCategories}>
              <View style={styles.categoriesGrid}>
                {Array.from(
                  { length: Math.ceil(categories.length / 2) },
                  (_, index) => renderCategoryPair(categories, index * 2)
                )}
              </View>
            </View>
          )}
        </View>
      </ScrollView>

      <View style={styles.selectedBanner}>
        {selectedCategory ? (
          <>
            <View style={styles.selectedIconContainer}>
              {selectedCategory.icon ? (
                renderIcon(selectedCategory.icon)
              ) : (
                <IconSymbol name="folder" size={24} color={theme.colors.text} />
              )}
            </View>
            <Text style={styles.selectedBannerText}>
              Categoría seleccionada: {selectedCategory.name}
            </Text>
          </>
        ) : (
          <Text style={styles.selectedBannerText}>
            No hay categoría seleccionada
          </Text>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  header: {
    padding: SPACING * 2,
    paddingTop: SPACING * 3,
    backgroundColor: theme.colors.primary,
    alignItems: "center",
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: "bold",
    color: theme.colors.background,
    textTransform: "uppercase",
    letterSpacing: 2,
  },
  mainActions: {
    padding: SPACING,
    gap: SPACING * 1.5,
  },
  actionCard: {
    backgroundColor: theme.colors.card,
    borderRadius: 16,
    padding: SPACING, // * 2,
    alignItems: "center",
    justifyContent: "center",
    elevation: 4,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  actionTitle: {
    fontSize: 22,
    fontWeight: "bold",
    color: theme.colors.text,
    marginTop: SPACING,
    textAlign: "center",
  },
  actionSubtitle: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    marginTop: 4,
    textAlign: "center",
  },
  expandedCategories: {
    marginTop: SPACING,
  },
  categoriesGrid: {
    width: "100%",
  },
  categoryRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: SPACING,
    width: "100%",
  },
  categoryCard: {
    width: "48%",
    backgroundColor: theme.colors.card,
    borderRadius: 12,
    padding: SPACING,
    alignItems: "center",
    elevation: 2,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
  },
  selectedCategoryCard: {
    borderWidth: 2,
    borderColor: theme.colors.primary,
  },
  iconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: theme.colors.background,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 8,
  },
  iconImage: {
    width: "90%",
    height: "90%",
    backgroundColor: "transparent", // Evitar fondo blanco
  },
  categoryCardTitle: {
    fontSize: 14,
    fontWeight: "600",
    color: theme.colors.text,
    textAlign: "center",
    marginTop: 8,
  },
  scrollContent: {
    flexGrow: 1,
  },
  expandIconContainer: {
    marginTop: SPACING,
    alignItems: "center",
  },
  expandIcon: {
    opacity: 0.8,
  },
  expandIconRotated: {
    transform: [{ rotate: "180deg" }],
  },
  selectedBanner: {
    flexDirection: "row",
    alignItems: "center",
    margin: SPACING,
    padding: SPACING,
    backgroundColor: theme.colors.card,
    borderRadius: 12,
    elevation: 3,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  selectedIconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: theme.colors.background,
    justifyContent: "center",
    alignItems: "center",
    marginRight: 12,
  },
  selectedBannerText: {
    flex: 1,
    fontSize: 16,
    fontWeight: "600",
    color: theme.colors.text,
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
    padding: SPACING * 2,
  },
  errorText: {
    fontSize: 16,
    color: theme.colors.error,
    textAlign: "center",
    marginBottom: 16,
  },
  retryButton: {
    paddingHorizontal: 24,
    paddingVertical: 12,
    backgroundColor: theme.colors.primary,
    borderRadius: 8,
  },
  retryText: {
    color: theme.colors.background,
    fontWeight: "600",
  },
});
