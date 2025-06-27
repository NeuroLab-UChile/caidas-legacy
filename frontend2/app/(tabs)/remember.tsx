import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
} from "react-native";
import apiService from "../services/apiService";
import { theme } from "@/src/theme";
import { IconSymbol } from "@/components/ui/IconSymbol";
import { ScrollView } from "react-native-gesture-handler";

interface TextRecommendation {
  id: number;
  data: string;
  category: string;
  sub_category: string;
  context_explanation: string;
  theme?: string;
  practic_data?: string;
  quote_link?: string;
  keywords?: string;
  learn?: string;
  remember?: string;
}

const RememberScreen = () => {
  const [recommendations, setRecommendations] = useState<TextRecommendation[]>(
    []
  );
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const [clickCount, setClickCount] = useState(0);
  const [hasMoreData, setHasMoreData] = useState(true);
  const [page, setPage] = useState(1);
  const flatListRef = React.useRef<FlatList>(null);

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async (refresh = false) => {
    try {
      setLoading(true);
      const response = await apiService.recommendations.getAll();

      if (response.data.recommendations.length === 0) {
        setHasMoreData(false);
        return;
      }

      if (refresh) {
        setRecommendations(response.data.recommendations);
        setPage(1);
        setHasMoreData(true);
      } else {
        setRecommendations((prev) => [
          ...prev,
          ...response.data.recommendations,
        ]);
        setPage((prev) => prev + 1);
      }
    } catch (err) {
      console.error("Error fetching recommendations:", err);
      setError("Error al cargar las recomendaciones");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchRecommendations(true);
  };

  const handleLoadMore = () => {
    if (!loading) {
      fetchRecommendations();
    }
  };

  const handleRecommendationPress = async (id: number) => {
    setExpandedId(expandedId === id ? null : id);

    try {
      if (expandedId !== id) {
        const newClickCount = clickCount + 1;
        setClickCount(newClickCount);

        const response = await apiService.recommendations.registerClick(id);

        // [JV] remove this 5 click refesh for now
        // if (newClickCount >= 5) {
        //   console.log("Reached 5 clicks, fetching new recommendations");
        //   handleRefresh();
        //   setClickCount(0);
        // } else
        if (response.data && response.data.more_recommendations) {
          setRecommendations(response.data.more_recommendations);
        }
      }
    } catch (err) {
      console.error("Error registering click:", err);
    }
  };

  // Función auxiliar para capitalizar la primera letra
  const capitalizeFirstLetter = (text: string) => {
    if (!text) return text;
    return text.charAt(0).toUpperCase() + text.slice(1);
  };

  const renderRecommendation = ({
    item,
    index,
  }: {
    item: TextRecommendation;
    index: number;
  }) => {
    const isExpanded = expandedId === item.id;

    // Determinar el tamaño de fuente basado en la longitud del texto
    const getFontSize = (text: string) => {
      if (text.length > 300) return 20; // Textos muy largos
      if (text.length > 200) return 24; // Textos largos
      if (text.length > 100) return 28; // Textos medianos
      if (text.length > 50) return 32; // Textos cortos
      return 36; // Textos muy cortos
    };

    return (
      <View style={styles.itemContainer}>
        <TouchableOpacity
          style={[
            styles.recommendationCard,
            { backgroundColor: theme.colors.primary },
          ]}
          onPress={() => handleRecommendationPress(item.id)}
        >
          <View style={styles.alignRight}>
            <Text
              style={[
                styles.recommendationText,
                {
                  color: theme.colors.text,
                  fontSize: getFontSize(item.data),
                  textAlign: "right",
                },
              ]}
            >
              {capitalizeFirstLetter(item.data)}
            </Text>

            {/* <Text
              style={[
                styles.categoryText,
                {
                  color: theme.colors.text,
                  textAlign: "right",
                },
              ]}
            >
              {capitalizeFirstLetter(item.category)}/
              {item.sub_category !== "nan"
                ? capitalizeFirstLetter(item.sub_category)
                : ""}
            </Text> */}
          </View>

          {isExpanded ? (
            <View
              style={[
                styles.explanationContainer,
                { backgroundColor: theme.colors.background },
              ]}
            >
              {item.context_explanation &&
                item.context_explanation !== "nan" && (
                  <Text
                    style={[
                      styles.explanationText,
                      { color: theme.colors.text },
                      { textAlign: "center" },
                    ]}
                  >
                    {item.context_explanation}
                  </Text>
                )}

              {/* {item.practic_data && item.practic_data !== "nan" && (
                <Text
                  style={[
                    styles.practicalText,
                    { color: theme.colors.text },
                    { textAlign: "center" },
                  ]}
                >
                  {"\n"}Práctica: {item.practic_data}
                </Text>
              )} */}

              {/* {item.keywords && item.keywords !== "nan" && (
                <Text
                  style={[styles.keywordsText, { color: theme.colors.text }]}
                >
                  {"\n"}Palabras clave: {item.keywords}
                </Text>
              )} */}

              {/* {item.quote_link && item.quote_link !== "nan" && (
                <Text style={[styles.sourceText, { color: theme.colors.text }]}>
                  {"\n"}Fuente: {item.quote_link}
                </Text>
              )} */}
            </View>
          ) : (
            <View style={styles.instructionContainer}>
              <IconSymbol
                name={isExpanded ? "chevron-up" : "chevron-down"}
                size={40}
                color={theme.colors.text}
              />
              <Text
                style={[styles.instructionText, { color: theme.colors.text }]}
              >
                {isExpanded ? "MOSTRAR MENOS" : "VER MÁS"}
              </Text>
            </View>
          )}
        </TouchableOpacity>
        {index < recommendations.length - 1 && (
          <View
            style={[
              styles.divider,
              { backgroundColor: theme.colors.text + "40" },
            ]}
          />
        )}
      </View>
    );
  };

  const scrollToTop = () => {
    flatListRef.current?.scrollToOffset({ offset: 0, animated: true });
  };

  const renderFooter = () => {
    if (loading) {
      return (
        <ActivityIndicator
          size="large"
          color={theme.colors.text}
          style={styles.loader}
        />
      );
    }

    if (!hasMoreData && recommendations.length > 0) {
      return (
        <View style={styles.endContainer}>
          <Text style={[styles.endText, { color: theme.colors.text }]}>
            Has llegado al final de las recomendaciones
          </Text>
          <TouchableOpacity
            style={styles.backToTopButton}
            onPress={scrollToTop}
          >
            <IconSymbol name="chevron.up" size={24} color={theme.colors.text} />
            <Text style={[styles.backToTopText, { color: theme.colors.text }]}>
              Volver arriba
            </Text>
          </TouchableOpacity>
        </View>
      );
    }

    return null;
  };

  if (loading) {
    return (
      <View
        style={[styles.container, { backgroundColor: theme.colors.primary }]}
      >
        <ActivityIndicator size="large" color={theme.colors.background} />
      </View>
    );
  }

  if (error) {
    return (
      <View
        style={[styles.container, { backgroundColor: theme.colors.primary }]}
      >
        <Text style={[styles.errorText, { color: theme.colors.background }]}>
          {error}
        </Text>
      </View>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.primary }]}>
      <FlatList
        ref={flatListRef}
        data={recommendations}
        renderItem={renderRecommendation}
        keyExtractor={(item, index) => `recommendation-${item.id}-${index}`}
        contentContainerStyle={styles.listContainer}
        style={{ backgroundColor: theme.colors.primary }}
        refreshing={refreshing}
        onRefresh={handleRefresh}
        onEndReached={() => hasMoreData && handleLoadMore()}
        onEndReachedThreshold={0.5}
        ListFooterComponent={renderFooter}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  listContainer: {
    flexGrow: 1,
  },
  itemContainer: {
    width: "100%",
  },
  recommendationCard: {
    padding: 32,
  },
  alignRight: {
    paddingLeft: "20%",
  },
  recommendationText: {
    fontFamily: "System",
    fontWeight: "bold",
    marginBottom: 24,
    lineHeight: 40,
  },
  categoryText: {
    fontSize: 20,
    fontFamily: "System",
    fontWeight: "600",
    marginBottom: 32,
    lineHeight: 28,
  },
  instructionContainer: {
    alignItems: "center",
    marginTop: 24,
    width: "100%",
  },
  instructionText: {
    fontSize: 20,
    textAlign: "center",
    fontFamily: "System",
    fontWeight: "600",
    marginTop: 12,
    lineHeight: 28,
  },
  explanationContainer: {
    marginTop: 24,
    padding: 24,
    borderRadius: 12,
    width: "100%",
  },
  explanationText: {
    fontSize: 24,
    fontFamily: "System",
    lineHeight: 36,
    fontWeight: "500",
  },
  practicalText: {
    fontSize: 24,
    fontFamily: "System",
    lineHeight: 36,
    marginTop: 16,
    fontWeight: "500",
  },
  divider: {
    height: 2,
    marginHorizontal: 24,
    marginVertical: 8,
    opacity: 0.5,
  },
  errorText: {
    textAlign: "center",
    fontSize: 24,
    fontFamily: "System",
    lineHeight: 32,
  },
  keywordsText: {
    fontSize: 20,
    fontFamily: "System",
    lineHeight: 28,
    marginTop: 16,
    fontWeight: "500",
    fontStyle: "italic",
  },
  sourceText: {
    fontSize: 16,
    fontFamily: "System",
    lineHeight: 24,
    marginTop: 16,
    fontWeight: "400",
    opacity: 0.8,
  },
  loader: {
    marginTop: 16,
  },
  endContainer: {
    padding: 24,
    alignItems: "center",
    justifyContent: "center",
  },
  endText: {
    fontSize: 16,
    textAlign: "center",
    marginBottom: 16,
    fontFamily: "System",
  },
  backToTopButton: {
    flexDirection: "row",
    alignItems: "center",
    padding: 12,
    borderRadius: 20,
    backgroundColor: "rgba(255,255,255,0.1)",
  },
  backToTopText: {
    marginLeft: 8,
    fontSize: 16,
    fontFamily: "System",
    fontWeight: "600",
  },
});

export default RememberScreen;
