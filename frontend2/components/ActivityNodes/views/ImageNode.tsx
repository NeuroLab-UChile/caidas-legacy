import React, { useState } from "react";
import {
  View,
  Image,
  Text,
  StyleSheet,
  ActivityIndicator,
  Dimensions,
  TouchableOpacity,
} from "react-native";
import { theme } from "@/src/theme";

interface ImageNodeViewProps {
  data: {
    id: number;
    description: string;
    type: string;
    media_url?: string;
  };
  onNext?: () => void;
}

export const ImageNodeView: React.FC<ImageNodeViewProps> = ({
  data,
  onNext,
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{data.description}</Text>

      <View style={styles.imageContainer}>
        {data.media_url && !error && (
          <Image
            source={{ uri: data.media_url }}
            style={styles.image}
            onLoadStart={() => setIsLoading(true)}
            onLoad={() => setIsLoading(false)}
            onError={() => {
              setError("Error al cargar la imagen");
              setIsLoading(false);
            }}
            resizeMode="contain"
          />
        )}

        {error && (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>Error: {error}</Text>
            {__DEV__ && (
              <Text style={styles.debugText}>
                URL de la imagen: {data.media_url || "No URL"}
              </Text>
            )}
          </View>
        )}
      </View>

      {onNext && (
        <TouchableOpacity
          style={styles.nextButton}
          onPress={() => {
            console.log("Navegando al siguiente desde ImageNodeView");
            onNext();
          }}
        >
          <Text style={styles.nextButtonText}>Continuar</Text>
        </TouchableOpacity>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  title: {
    fontSize: 16,
    fontWeight: "500",
    marginBottom: 16,
    color: theme.colors.text,
  },
  imageContainer: {
    width: Dimensions.get("window").width - 32,
    aspectRatio: 16 / 9,
    backgroundColor: "#000",
    borderRadius: 8,
    overflow: "hidden",
    position: "relative",
  },
  image: {
    width: "100%",
    height: "100%",
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
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 16,
  },
  errorText: {
    color: theme.colors.error,
    textAlign: "center",
    marginBottom: 8,
  },
  debugText: {
    color: theme.colors.text,
    fontSize: 12,
    textAlign: "center",
  },
  nextButton: {
    backgroundColor: theme.colors.primary,
    padding: 16,
    borderRadius: 8,
    alignItems: "center",
    marginTop: 20,
    marginHorizontal: 16,
  },
  nextButtonText: {
    color: "white",
    fontSize: 16,
    fontWeight: "600",
  },
});
