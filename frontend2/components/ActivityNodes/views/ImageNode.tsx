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
import { TextWithHyperlinks } from "@/components/ui/TextWithHyperlinks";
import React from "react";
import { Modal, Pressable, TouchableOpacity, ScrollView } from "react-native";

interface ImageNodeViewProps {
  data: {
    id: number;
    title: string;
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
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const imageUrl = data?.media_url || "";
  console.log("ImageNodeView data:", data);

  const description = data.description ? (
    <TextWithHyperlinks>{data.description}</TextWithHyperlinks>
  ) : null;

  const [modalVisible, setModalVisible] = useState(false);

  const handleImagePress = () => {
    console.warn("Image pressed");
    if (imageUrl) {
      console.log("Opening image in modal:", imageUrl);
      setModalVisible(true);
    }
  };

  const handleCloseModal = () => {
    setModalVisible(false);
  };

  const EnlargedImageModal = () => (
    <Modal
      visible={modalVisible}
      transparent={true}
      animationType="fade"
      onRequestClose={handleCloseModal}
    >
      <View style={{ flex: 1, backgroundColor: "rgba(0,0,0,0.95)" }}>
        <TouchableOpacity
          style={{
            position: "absolute",
            top: 40,
            right: 24,
            zIndex: 2,
            backgroundColor: "rgba(0,0,0,0.5)",
            borderRadius: 20,
            padding: 8,
          }}
          onPress={handleCloseModal}
          accessibilityLabel="Cerrar imagen ampliada"
        >
          <Text style={{ color: "#fff", fontSize: 24 }}>✕</Text>
        </TouchableOpacity>
        <ScrollView
          style={{ flex: 1 }}
          contentContainerStyle={{
            flex: 1,
            justifyContent: "center",
            alignItems: "center",
          }}
          maximumZoomScale={4}
          minimumZoomScale={1}
          centerContent={true}
          bouncesZoom={true}
        >
          <Image
            source={{ uri: imageUrl }}
            style={{
              width: Dimensions.get("window").width,
              height: Dimensions.get("window").width * 0.5625,
              resizeMode: "contain",
            }}
          />
        </ScrollView>
      </View>
    </Modal>
  );

  return (
    <View style={styles.container}>
      <EnlargedImageModal />

      <Text style={styles.title}>{data.title}</Text>
      {/* {data.description && (
        <Text style={styles.description}>{data.description}</Text>
      )} */}
      {description}

      <View style={styles.imageContainer}>
        {imageUrl ? (
          <TouchableOpacity onPress={handleImagePress} style={styles.image}>
            <Image
              source={{ uri: imageUrl }}
              style={{ width: "100%", height: "100%" }}
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
          </TouchableOpacity>
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
              <Text style={styles.debugText}>URL: {imageUrl || "No URL"}</Text>
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
    fontSize: 24,
    fontWeight: "bold",
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
