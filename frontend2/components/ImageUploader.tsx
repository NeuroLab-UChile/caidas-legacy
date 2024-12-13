import React from "react";
import { TouchableOpacity, StyleSheet, View, Text, Alert } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import * as ImagePicker from "expo-image-picker";

interface ImageUploaderProps {
  onImageSelected: (uri: string) => void;
}

export function ImageUploader({ onImageSelected }: ImageUploaderProps) {
  const showImageSourceOptions = () => {
    Alert.alert("Seleccionar foto", "¿De dónde quieres seleccionar la foto?", [
      {
        text: "Cámara",
        onPress: () => takePhoto(),
      },
      {
        text: "Galería",
        onPress: () => pickImage(),
      },
      {
        text: "Cancelar",
        style: "cancel",
      },
    ]);
  };

  const takePhoto = async () => {
    // Pedir permiso de cámara
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== "granted") {
      Alert.alert("Se necesita permiso para acceder a la cámara");
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      aspect: [1, 1],
      quality: 1,
    });

    if (!result.canceled && result.assets[0].uri) {
      onImageSelected(result.assets[0].uri);
    }
  };

  const pickImage = async () => {
    // Pedir permiso de galería
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== "granted") {
      Alert.alert("Se necesita permiso para acceder a la galería");
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 1,
    });

    if (!result.canceled && result.assets[0].uri) {
      onImageSelected(result.assets[0].uri);
    }
  };

  return (
    <TouchableOpacity
      onPress={showImageSourceOptions}
      style={styles.container}
      activeOpacity={0.7}
    >
      <View style={styles.iconContainer}>
        <Ionicons name="camera" size={24} color="white" style={styles.icon} />
        <Text style={styles.text}>Subir foto</Text>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    width: "100%",
    height: "100%",
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "rgba(0,0,0,0.1)",
    borderRadius: 60,
  },
  iconContainer: {
    backgroundColor: "rgba(0,0,0,0.7)",
    padding: 12,
    borderRadius: 20,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
  },
  icon: {
    marginRight: 8,
  },
  text: {
    color: "white",
    fontSize: 16,
    fontWeight: "500",
  },
});
