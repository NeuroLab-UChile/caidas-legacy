import React, { useState } from "react";
import { View, Text, StyleSheet, TouchableOpacity, Image } from "react-native";
import { ScrollView } from "react-native";
import * as ImagePicker from "expo-image-picker";
import { Ionicons } from "@expo/vector-icons";
import { theme } from "@/src/theme";

interface ImageQuestionProps {
  data: {
    id: number;
    type: string;

    question: string;
    description?: string;
    image?: string;
  };
  setResponse: (response: { image: string } | null) => void;
}

export function ImageQuestionView({ data, setResponse }: ImageQuestionProps) {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);

  const handleSelectImage = async () => {
    try {
      const { status } =
        await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== "granted") {
        alert("Se necesitan permisos para acceder a la galería");
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [1, 1],
        quality: 0.7,
      });

      if (!result.canceled && result.assets && result.assets[0]) {
        setSelectedImage(result.assets[0].uri);
        setResponse({ image: result.assets[0].uri });
      }
    } catch (error) {
      console.error("Error al seleccionar imagen:", error);
      alert("Error al seleccionar la imagen");
    }
  };

  const handleTakePhoto = async () => {
    try {
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      if (status !== "granted") {
        alert("Se necesitan permisos para usar la cámara");
        return;
      }

      const result = await ImagePicker.launchCameraAsync({
        allowsEditing: true,
        aspect: [1, 1],
        quality: 0.7,
      });

      if (!result.canceled && result.assets && result.assets[0]) {
        setSelectedImage(result.assets[0].uri);
        setResponse({ image: result.assets[0].uri });
      }
    } catch (error) {
      console.error("Error al tomar foto:", error);
      alert("Error al tomar la foto");
    }
  };

  const handleChangeImage = () => {
    setSelectedImage(null);
    setResponse(null);
  };

  if (!data) {
    console.error("Missing required data in ImageQuestionView");
    return null;
  }

  return (
    <View style={theme.components.node.container}>
      <Text style={theme.components.node.question}>{data.question}</Text>

      {selectedImage ? (
        <View style={styles.selectedImageContainer}>
          <Image
            source={{ uri: selectedImage }}
            style={styles.selectedImage}
            resizeMode="cover"
          />
          <TouchableOpacity
            style={[theme.components.node.optionButton, styles.changeButton]}
            onPress={handleChangeImage}
          >
            <Text style={styles.buttonText}>Cambiar imagen</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <View style={styles.optionsContainer}>
          {[
            {
              icon: "images",
              text: "Seleccionar de Galería",
              onPress: handleSelectImage,
            },
            { icon: "camera", text: "Tomar Foto", onPress: handleTakePhoto },
          ].map((option, index) => (
            <TouchableOpacity
              key={index}
              style={theme.components.node.optionButton}
              onPress={option.onPress}
            >
              <View style={theme.components.node.optionContent}>
                <Ionicons
                  name={option.icon as any}
                  size={24}
                  color={theme.colors.text}
                />
                <Text style={theme.components.node.optionText}>
                  {option.text}
                </Text>
              </View>
            </TouchableOpacity>
          ))}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    gap: 12,
  },
  question: {
    fontSize: 20,
    fontWeight: "600",
    color: theme.colors.text,
    marginBottom: 24,
    lineHeight: 28,
  },
  optionsContainer: {
    gap: 12,
  },
  optionButton: {
    padding: 16,
    borderRadius: 12,
    backgroundColor: theme.colors.background,
    borderWidth: 2,
    borderColor: theme.colors.border,
  },
  optionContent: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  optionText: {
    fontSize: 16,
    color: theme.colors.text,
  },
  selectedImageContainer: {
    alignItems: "center",
    gap: 12,
  },
  selectedImage: {
    width: "100%",
    aspectRatio: 1,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: theme.colors.primary,
  },
  changeButton: {
    padding: 16,
    borderRadius: 12,
    backgroundColor: theme.colors.background,
    borderWidth: 2,
    borderColor: theme.colors.primary,
  },
  buttonText: {
    fontSize: 16,
    color: theme.colors.text,
    fontWeight: "600",
    textAlign: "center",
  },
});
