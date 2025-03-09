import * as ImagePicker from "expo-image-picker";
import * as FileSystem from 'expo-file-system';

interface ImagePickerOptions {
  aspect?: [number, number];
  quality?: number;
}

export const useImagePicker = () => {
  const convertToBase64 = async (uri: string): Promise<string> => {
    try {
      const base64 = await FileSystem.readAsStringAsync(uri, {
        encoding: FileSystem.EncodingType.Base64
      });
      return `data:image/jpeg;base64,${base64}`;
    } catch (error) {
      console.error('Error converting to base64:', error);
      throw error;
    }
  };

  const pickImage = async (options: ImagePickerOptions = {}) => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== "granted") {
      throw new Error("Se necesitan permisos para acceder a la galería");
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: options.aspect || [1, 1],
      quality: options.quality || 0.7,
      base64: true,
    });

    if (!result.canceled && result.assets && result.assets[0]) {
      return await convertToBase64(result.assets[0].uri);
    }
    return null;
  };

  const takePhoto = async (options: ImagePickerOptions = {}) => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== "granted") {
      throw new Error("Se necesitan permisos para usar la cámara");
    }

    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      aspect: options.aspect || [1, 1],
      quality: options.quality || 0.7,
      base64: true,
    });

    if (!result.canceled && result.assets && result.assets[0]) {
      return await convertToBase64(result.assets[0].uri);
    }
    return null;
  };

  return {
    pickImage,
    takePhoto,
    convertToBase64
  };
}; 