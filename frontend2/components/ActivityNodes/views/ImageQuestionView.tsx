import React, { useState } from "react";
import { View, Text, StyleSheet, TouchableOpacity, Image } from "react-native";

import { ImageUploader } from "@/components/ImageUploader";
import { theme } from "@/src/theme";

interface ImageQuestionProps {
  data: {
    question: string;
    image?: string;
  };
  onNext?: (response: { image: string }) => void;
}

export function ImageQuestionView({ data, onNext }: ImageQuestionProps) {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);

  const handleImageSelected = (uri: string) => {
    setSelectedImage(uri);
  };

  return (
    <View style={styles.container}>
      <Text
        style={[theme.typography.styles.body1, { color: theme.colors.text }]}
      >
        {data.question}
      </Text>

      <View style={styles.imageContainer}>
        {selectedImage ? (
          <View style={styles.selectedImageContainer}>
            <Image
              source={{ uri: selectedImage }}
              style={styles.selectedImage}
              resizeMode="cover"
            />
            <TouchableOpacity
              style={styles.changeImageButton}
              onPress={() => setSelectedImage(null)}
            >
              <Text
                style={[
                  theme.typography.styles.button,
                  { color: theme.colors.primary },
                ]}
              >
                Cambiar imagen
              </Text>
            </TouchableOpacity>
          </View>
        ) : (
          <View style={styles.uploaderContainer}>
            <ImageUploader onImageSelected={handleImageSelected} />
          </View>
        )}
      </View>

      <TouchableOpacity
        style={[
          theme.components.button.variants.primary,
          { opacity: selectedImage ? 1 : 0.5 },
        ]}
        onPress={() => selectedImage && onNext?.({ image: selectedImage })}
        disabled={!selectedImage}
      >
        <Text style={theme.typography.styles.button}>Continuar</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  imageContainer: {
    marginVertical: 24,
    alignItems: "center",
  },
  uploaderContainer: {
    width: "100%",
    aspectRatio: 1,
    maxHeight: 300,
    borderRadius: 12,
    overflow: "hidden",
  },
  selectedImageContainer: {
    width: "100%",
    alignItems: "center",
  },
  selectedImage: {
    width: "100%",
    aspectRatio: 1,
    maxHeight: 300,
    borderRadius: 12,
  },
  changeImageButton: {
    marginTop: 12,
    padding: 8,
  },
});
