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
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      const { data } = await apiService.recommendations.getAll();

      setRecommendations(data as TextRecommendation[]);
    } catch (err) {
      console.error("Error fetching recommendations:", err);
      setError("Error al cargar las recomendaciones");
    } finally {
      setLoading(false);
    }
  };

  const handleRecommendationPress = (id: number) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const renderRecommendation = ({
    item,
    index,
  }: {
    item: TextRecommendation;
    index: number;
  }) => {
    const isExpanded = expandedId === item.id;

    return (
      <View style={styles.itemContainer}>
        <TouchableOpacity
          style={[
            styles.recommendationCard,
            { backgroundColor: theme.colors.primary },
          ]}
          onPress={() => handleRecommendationPress(item.id)}
        >
          <Text
            style={[styles.recommendationText, { color: theme.colors.text }]}
          >
            {item.data}
          </Text>
          <Text style={[styles.categoryText, { color: theme.colors.text }]}>
            //{item.category}/
            {item.sub_category !== "nan" ? item.sub_category : ""}
          </Text>

          {isExpanded ? (
            <View
              style={[
                styles.explanationContainer,
                { backgroundColor: theme.colors.text },
              ]}
            >
              {item.context_explanation &&
                item.context_explanation !== "nan" && (
                  <Text
                    style={[
                      styles.explanationText,
                      { color: theme.colors.primary },
                    ]}
                  >
                    {item.context_explanation}
                  </Text>
                )}

              {item.practic_data && item.practic_data !== "nan" && (
                <Text
                  style={[
                    styles.practicalText,
                    { color: theme.colors.primary },
                  ]}
                >
                  {"\n"}Práctica: {item.practic_data}
                </Text>
              )}

              {item.keywords && item.keywords !== "nan" && (
                <Text
                  style={[styles.keywordsText, { color: theme.colors.primary }]}
                >
                  {"\n"}Palabras clave: {item.keywords}
                </Text>
              )}

              {item.quote_link && item.quote_link !== "nan" && (
                <Text
                  style={[styles.sourceText, { color: theme.colors.primary }]}
                >
                  {"\n"}Fuente: {item.quote_link}
                </Text>
              )}
            </View>
          ) : (
            <View style={styles.instructionContainer}>
              <IconSymbol
                name={isExpanded ? "chevron.up" : "chevron.down"}
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
        data={recommendations}
        renderItem={renderRecommendation}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.listContainer}
        style={{ backgroundColor: theme.colors.primary }}
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
    alignItems: "center",
  },
  recommendationText: {
    fontSize: 32,
    textAlign: "center",
    fontFamily: "System",
    fontWeight: "bold",
    marginBottom: 24,
    lineHeight: 40,
  },
  categoryText: {
    fontSize: 20,
    textAlign: "center",
    fontFamily: "System",
    fontWeight: "600",
    marginBottom: 32,
    lineHeight: 28,
  },
  instructionContainer: {
    alignItems: "center",
    marginTop: 24,
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
});

export default RememberScreen;
