import { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  ActivityIndicator,
  TouchableOpacity,
  Alert,
  Dimensions,
} from "react-native";

import { ImageUploader } from "../../components/ImageUploader";
import { Ionicons } from "@expo/vector-icons";
import apiService from "../services/apiService";
import { theme } from "../../src/theme";
import * as ImagePicker from "expo-image-picker";
import * as FileSystem from 'expo-file-system';
import { useImagePicker } from '../../hooks/useImagePicker';

const { width } = Dimensions.get("window");

export default function ProfileScreen() {
  const [user, setUser] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const { convertToBase64 } = useImagePicker();

  const loadProfile = async () => {
    try {
      const response = await apiService.user.getProfile();
      console.log("response", response);
      setUser(response.data);
    } catch (error) {
      console.error("Error al cargar perfil:", error);
    } finally {
      setIsInitialLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, []);

  const handleImageSelected = async (uri: string) => {
    try {
      setIsLoading(true);
      console.log("Subiendo imagen:", uri);

      // Usamos el convertToBase64 del hook
      const base64Image = await convertToBase64(uri);
      console.log("Imagen convertida a base64");

      const response = await apiService.user.uploadProfileImage({
        image: base64Image
      });
      
      console.log("Respuesta de subida:", response.data);

      if (response.data?.profile?.profile_image) {
        const timestamp = new Date().getTime();
        const imageUrlWithTimestamp = `${response.data.profile.profile_image}?t=${timestamp}`;
        setUser((prev: any) => ({
          ...prev,
          profile: {
            ...prev.profile,
            profile_image: imageUrlWithTimestamp,
          },
        }));
      }

      await loadProfile();
    } catch (error) {
      console.error("Error al subir la imagen:", error);
      Alert.alert(
        "Error",
        "No se pudo subir la imagen. Por favor, intenta de nuevo."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleImageOptions = () => {
    Alert.alert(
      "Opciones",
      "¿Qué deseas hacer con la imagen?",
      [
        {
          text: "Cambiar",
          onPress: () => {
            showImageSourceOptions();
          },
        },
        {
          text: "Eliminar",
          onPress: async () => {
            try {
              setIsLoading(true);
              const response = await apiService.user.deleteProfileImage();
              setUser(response.data);
            } catch (error) {
              console.error("Error al eliminar la imagen:", error);
              Alert.alert("Error", "No se pudo eliminar la imagen");
            } finally {
              setIsLoading(false);
            }
          },
        },
        {
          text: "Cancelar",
          style: "cancel",
        },
      ],
      { cancelable: false }
    );
  };

  const showImageSourceOptions = () => {
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
            quality: 1,
          });

          if (!result.canceled && result.assets[0].uri) {
            handleImageSelected(result.assets[0].uri);
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
            quality: 1,
          });

          if (!result.canceled && result.assets[0].uri) {
            handleImageSelected(result.assets[0].uri);
          }
        },
      },
      {
        text: "Cancelar",
        style: "cancel",
      },
    ]);
  };

  if (isInitialLoading) {
    return (
      <View style={[styles.container, styles.cardContent]}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: theme.colors.background }]}
      contentContainerStyle={styles.profileContent}
    >
      <View
        style={[
          styles.headerBackground,
          { backgroundColor: theme.colors.primary },
        ]}
      />

      <View style={styles.profileContent}>
        <View style={styles.profileImageSection}>
          <TouchableOpacity
            style={styles.imageContainer}
            onPress={user?.profile?.profile_image ? handleImageOptions : showImageSourceOptions}
            activeOpacity={0.7}
          >
            {user?.profile?.profile_image ? (
              <>
                <Image
                  key={user?.profile?.profile_image}
                  source={{
                    uri: user?.profile?.profile_image,
                    cache: 'reload',
                  }}
                  style={styles.existingImage}
                  onError={(e) => console.log('Error loading image:', e.nativeEvent.error)}
                />
                <View style={styles.editButton}>
                  <Ionicons name="pencil" size={16} color="black" />
                </View>
              </>
            ) : (
              <View
                style={[
                  styles.placeholderImage,
                  { backgroundColor: theme.colors.border },
                ]}
              >
                <Ionicons 
                  name="person-circle-outline" 
                  size={60} 
                  color={theme.colors.text}
                />
              </View>
            )}
          </TouchableOpacity>

          <Text style={[styles.username, { color: theme.colors.text }]}>
            {user?.username || "Usuario"}
          </Text>
          <Text style={[styles.email, { color: theme.colors.text }]}>
            {user?.email || "Email no especificado"}
          </Text>
        </View>

        <View style={styles.infoSection}>
          <View
            style={[styles.infoCard, { backgroundColor: theme.colors.card }]}
          >
            <View style={styles.cardHeader}>
              <Ionicons
                name="person-outline"
                size={24}
                color={theme.colors.text}
              />
              <Text style={[styles.cardTitle, { color: theme.colors.text }]}>
                Información Personal
              </Text>
            </View>

            <View style={styles.cardContent}>
              <View style={styles.infoRow}>
                <Text style={[styles.label, { color: theme.colors.text }]}>
                  Nombre
                </Text>
                <Text style={[styles.value, { color: theme.colors.text }]}>
                  {user?.first_name || "No especificado"}
                </Text>
              </View>

              <View style={styles.infoRow}>
                <Text style={[styles.label, { color: theme.colors.text }]}>
                  Apellido
                </Text>
                <Text style={[styles.value, { color: theme.colors.text }]}>
                  {user?.last_name || "No especificado"}
                </Text>
              </View>
            </View>
          </View>

          <View
            style={[styles.infoCard, { backgroundColor: theme.colors.card }]}
          >
            <View style={styles.cardHeader}>
              <Ionicons
                name="call-outline"
                size={24}
                color={theme.colors.text}
              />
              <Text style={[styles.cardTitle, { color: theme.colors.text }]}>
                Contacto
              </Text>
            </View>

            <View style={styles.cardContent}>
              <View style={styles.infoRow}>
                <Text style={[styles.label, { color: theme.colors.text }]}>
                  Email
                </Text>
                <Text style={[styles.value, { color: theme.colors.text }]}>
                  {user?.email || "No especificado"}
                </Text>
              </View>

              <View style={styles.infoRow}>
                <Text style={[styles.label, { color: theme.colors.text }]}>
                  Teléfono
                </Text>
                <Text style={[styles.value, { color: theme.colors.text }]}>
                  {user?.profile?.phone || "No especificado"}
                </Text>
              </View>
            </View>
          </View>
        </View>
      </View>

      {isLoading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  headerBackground: {
    height: 150,
    width: "100%",
    position: "absolute",
    top: 0,
  },
  profileContent: {
    flex: 1,
    paddingTop: 20,
  },
  profileImageSection: {
    alignItems: "center",
    marginBottom: 30,
  },
  imageContainer: {
    width: 120,
    height: 120,
    marginBottom: 15,
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 4.65,
    elevation: 8,
  },
  existingImage: {
    width: "100%",
    height: "100%",
    borderRadius: 60,
    borderWidth: 3,
    borderColor: "white",
    backgroundColor: theme.colors.border,
  },
  placeholderImage: {
    width: "100%",
    height: "100%",
    borderRadius: 60,
    justifyContent: "center",
    alignItems: "center",
    borderWidth: 3,
    borderColor: "white",
  },
  editButton: {
    position: "absolute",
    bottom: 5,
    right: 5,
    backgroundColor: "white",
    padding: 8,
    borderRadius: 15,
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  username: {
    fontSize: 24,
    fontWeight: "bold",
    marginBottom: 5,
  },
  email: {
    fontSize: 16,
    opacity: 0.7,
    marginBottom: 20,
  },
  infoSection: {
    paddingHorizontal: 20,
  },
  infoCard: {
    borderRadius: 15,
    marginBottom: 20,
    padding: 20,
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  cardHeader: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 15,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: "600",
    marginLeft: 10,
  },
  cardContent: {
    marginLeft: 34,
  },
  infoRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: "rgba(0,0,0,0.05)",
  },
  label: {
    fontSize: 16,
    opacity: 0.8,
  },
  value: {
    fontSize: 16,
    fontWeight: "500",
  },
  loadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: "rgba(0,0,0,0.3)",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 1000,
  },
});