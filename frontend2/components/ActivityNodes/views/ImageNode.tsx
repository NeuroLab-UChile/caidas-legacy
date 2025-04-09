import { useState } from "react";
import {
  View,
  Image,
  Text,
  StyleSheet,
  ActivityIndicator,
  Dimensions,
} from "react-native";
import { theme } from "@/src/theme";

interface ImageNodeViewProps {
  data: {
    id: number;
    content: string;
    type: string;
    media_url?: string;
    description?: string;
  };
  onNext?: () => void;
}

export const ImageNodeView: React.FC<ImageNodeViewProps> = ({
  data,
  onNext,
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const imageUrl = data?.media_url || '';

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{data.content}</Text>
      {data.description && (
        <Text style={styles.description}>{data.description}</Text>
      )}

      <View style={styles.imageContainer}>
        {imageUrl ? (
          <Image
            source={{ uri: imageUrl }}
            style={styles.image}
            onLoadStart={() => {
              setIsLoading(true);
              setError(null);
            }}
            onLoad={() => {
              setIsLoading(false);
            }}
            onError={() => {
              setError("No se pudo cargar la imagen");
              setIsLoading(false);
            }}
            resizeMode="contain"
          />
        ) : (
          <View style={styles.placeholderContainer}>
            <Text style={styles.placeholderText}>Sin imagen disponible</Text>
          </View>
        )}

        {isLoading && (
          <View style={styles.loadingOverlay}>
            <ActivityIndicator size="large" color={theme.colors.primary} />
            <Text style={styles.loadingText}>Cargando imagen...</Text>
          </View>
        )}

        {error && (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>{error}</Text>
            {__DEV__ && (
              <Text style={styles.debugText}>
                URL: {imageUrl || "No URL"}
              </Text>
            )}
          </View>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  title: {
    fontSize: 18,
    fontWeight: "600",
    marginBottom: 8,
    color: theme.colors.text,
    textAlign: "center",
  },
  description: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginBottom: 16,
    textAlign: "center",
  },
  imageContainer: {
    width: Dimensions.get("window").width - 32,
    aspectRatio: 16 / 9,
    backgroundColor: theme.colors.background,
    borderRadius: 12,
    overflow: "hidden",
    position: "relative",
    justifyContent: "center",
    alignItems: "center",
  },
  image: {
    width: "100%",
    height: "100%",
  },
  placeholderContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: theme.colors.surface,
  },
  placeholderText: {
    color: theme.colors.textSecondary,
    fontSize: 16,
  },
  loadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: "rgba(0,0,0,0.3)",
    justifyContent: "center",
    alignItems: "center",
  },
  loadingText: {
    color: "#fff",
    marginTop: 8,
  },
  errorContainer: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "rgba(255,0,0,0.1)",
    padding: 16,
  },
  errorText: {
    color: theme.colors.error,
    textAlign: "center",
    fontSize: 16,
    marginBottom: 8,
  },
  debugText: {
    color: theme.colors.text,
    fontSize: 12,
    textAlign: "center",
  },
});
