import { TouchableOpacity, StyleSheet, View, Text, Alert } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import * as ImagePicker from "expo-image-picker";
import { theme } from "@/src/theme";

interface ImageUploaderProps {
  onImageSelected: (base64Image: string) => void;
}

export function ImageUploader({ onImageSelected }: ImageUploaderProps) {
  const showImageSourceOptions = async () => {
    Alert.alert("Seleccionar foto", "¿De dónde quieres seleccionar la foto?", [
      {
        text: "Cámara",
        onPress: async () => {
          const { status } = await ImagePicker.requestCameraPermissionsAsync();
          if (status !== "granted") {
            Alert.alert("Se necesita permiso para acceder a la cámara");
            return;
          }

          const result = await ImagePicker.launchCameraAsync({
            allowsEditing: true,
            aspect: [1, 1],
            quality: 0.5,
            base64: true,
          });

          if (!result.canceled && result.assets[0]) {
            const base64Image = `data:image/jpeg;base64,${result.assets[0].base64}`;
            onImageSelected(base64Image);
          }
        },
      },
      {
        text: "Galería",
        onPress: async () => {
          const { status } =
            await ImagePicker.requestMediaLibraryPermissionsAsync();
          if (status !== "granted") {
            Alert.alert("Se necesita permiso para acceder a la galería");
            return;
          }

          const result = await ImagePicker.launchImageLibraryAsync({
            mediaTypes: ImagePicker.MediaTypeOptions.Images,
            allowsEditing: true,
            aspect: [1, 1],
            quality: 0.5,
            base64: true,
          });

          if (!result.canceled && result.assets[0]) {
            const base64Image = `data:image/jpeg;base64,${result.assets[0].base64}`;
            onImageSelected(base64Image);
          }
        },
      },
      {
        text: "Cancelar",
        style: "cancel",
      },
    ]);
  };

  return (
    <TouchableOpacity onPress={showImageSourceOptions}>
      <Ionicons name="camera" size={40} color={theme.colors.text} />
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
