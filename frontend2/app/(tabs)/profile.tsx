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
  Linking,
  Button,
  TextInput,
} from "react-native";

import { ImageUploader } from "../../components/ImageUploader";
import { Ionicons } from "@expo/vector-icons";
import apiService from "../services/apiService";
import { theme } from "../../src/theme";
import * as ImagePicker from "expo-image-picker";
import * as FileSystem from "expo-file-system";
import { useImagePicker } from "../../hooks/useImagePicker";
import { useFocusEffect } from "@react-navigation/native";
import { useCallback } from "react";
import CustomisableAlert, {
  showAlert,
  closeAlert,
} from "react-native-customisable-alert";

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

  useFocusEffect(
    useCallback(() => {
      apiService.activityLog.trackAction("screen perfil"); // Record action
    }, [])
  );

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
        image: base64Image,
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
    // Alert.alert(
    //   "Opciones",
    //   "¿Qué deseas hacer con la imagen?",
    //   [
    //     {
    //       text: "Cambiar",
    //       onPress: () => {
    //         showImageSourceOptions();
    //       },
    //     },
    //     {
    //       text: "Eliminar",
    //       onPress: async () => {
    //         try {
    //           setIsLoading(true);
    //           const response = await apiService.user.deleteProfileImage();
    //           setUser(response.data);
    //         } catch (error) {
    //           console.error("Error al eliminar la imagen:", error);
    //           Alert.alert("Error", "No se pudo eliminar la imagen");
    //         } finally {
    //           setIsLoading(false);
    //         }
    //       },
    //     },
    //     {
    //       text: "Cancelar",
    //       style: "cancel",
    //     },
    //   ],
    //   { cancelable: false }
    // );

    showAlert({
      title: "Qué deseas hacer con la imagen?",
      message: "",
      alertType: "custom",
      customAlert: (
        <View style={{ backgroundColor: "white", padding: 20, width: "85%" }}>
          <Text
            style={{
              textAlign: "center",
              fontSize: theme.typography.sizes.headline1,
              fontWeight: "bold",
              marginBottom: 20,
              // color: "white",
            }}
          >
            Qué deseas hacer con la imagen?
          </Text>
          <View
            style={{
              flexDirection: "row",
              justifyContent: "space-evenly",
              marginTop: 30,
            }}
          >
            <TouchableOpacity
              onPress={showImageSourceOptions}
              style={{
                backgroundColor: "orange",
                paddingVertical: 10,
                paddingHorizontal: 25,
                borderRadius: 8,
              }}
            >
              <Text
                style={{
                  fontSize: theme.typography.sizes.body1,
                  color: "white",
                  fontWeight: "bold",
                }}
              >
                Cambiar
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={async () => {
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
                closeAlert();
              }}
              style={{
                backgroundColor: "red",
                paddingVertical: 10,
                paddingHorizontal: 25,
                borderRadius: 8,
              }}
            >
              <Text
                style={{
                  fontSize: theme.typography.sizes.body1,
                  color: "white",
                  fontWeight: "bold",
                }}
              >
                Eliminar
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={() => closeAlert()}
              style={{
                backgroundColor: theme.colors.border,
                paddingVertical: 10,
                paddingHorizontal: 25,
                borderRadius: 8,
              }}
            >
              <Text
                style={{
                  fontSize: theme.typography.sizes.body1,
                  color: theme.colors.text,
                  fontWeight: "bold",
                }}
              >
                Cancelar
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      ),
    });
  };

  const showImageSourceOptions = () => {
    //   Alert.alert("Seleccionar foto", "¿De dónde quieres seleccionar la foto?", [
    //     {
    //       text: "Cámara",
    //       onPress: async () => {
    //         const { status } = await ImagePicker.requestCameraPermissionsAsync();
    //         if (status !== "granted") {
    //           Alert.alert("Se necesita permiso para acceder a la cámara");
    //           return;
    //         }

    //         const result = await ImagePicker.launchCameraAsync({
    //           // allowsEditing: true,
    //           // aspect: [1, 1],
    //           quality: 1,
    //         });

    //         if (!result.canceled && result.assets[0].uri) {
    //           handleImageSelected(result.assets[0].uri);
    //         }
    //       },
    //     },
    //     {
    //       text: "Galería",
    //       onPress: async () => {
    //         const { status } =
    //           await ImagePicker.requestMediaLibraryPermissionsAsync();
    //         if (status !== "granted") {
    //           Alert.alert("Se necesita permiso para acceder a la galería");
    //           return;
    //         }

    //         const result = await ImagePicker.launchImageLibraryAsync({
    //           mediaTypes: ImagePicker.MediaTypeOptions.Images,
    //           // allowsEditing: true,
    //           // aspect: [1, 1],
    //           quality: 1,
    //         });

    //         if (!result.canceled && result.assets[0].uri) {
    //           handleImageSelected(result.assets[0].uri);
    //         }
    //       },
    //     },
    //     {
    //       text: "Cancelar",
    //       style: "cancel",
    //     },
    //   ]);

    showAlert({
      title: "Seleccionar foto",
      message: "",
      alertType: "custom",
      customAlert: (
        <View style={{ backgroundColor: "white", padding: 20, width: "85%" }}>
          <Text
            style={{
              textAlign: "center",
              fontSize: theme.typography.sizes.headline1,
              fontWeight: "bold",
              marginBottom: 20,
              // color: "white",
            }}
          >
            De dónde quieres seleccionar la foto?
          </Text>
          <View
            style={{
              flexDirection: "row",
              justifyContent: "space-evenly",
              marginTop: 30,
            }}
          >
            <TouchableOpacity
              onPress={async () => {
                const { status } =
                  await ImagePicker.requestCameraPermissionsAsync();
                if (status !== "granted") {
                  Alert.alert("Se necesita permiso para acceder a la cámara");
                  return;
                }

                const result = await ImagePicker.launchCameraAsync({
                  // allowsEditing: true,
                  // aspect: [1, 1],
                  quality: 1,
                });

                if (!result.canceled && result.assets[0].uri) {
                  handleImageSelected(result.assets[0].uri);
                }
                closeAlert();
              }}
              style={{
                backgroundColor: "orange",
                paddingVertical: 10,
                paddingHorizontal: 25,
                borderRadius: 8,
              }}
            >
              <Text
                style={{
                  fontSize: theme.typography.sizes.body1,
                  color: "white",
                  fontWeight: "bold",
                }}
              >
                Cámara
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={async () => {
                const { status } =
                  await ImagePicker.requestMediaLibraryPermissionsAsync();
                if (status !== "granted") {
                  Alert.alert("Se necesita permiso para acceder a la galería");
                  return;
                }

                const result = await ImagePicker.launchImageLibraryAsync({
                  mediaTypes: ImagePicker.MediaTypeOptions.Images,
                  // allowsEditing: true,
                  // aspect: [1, 1],
                  quality: 1,
                });

                if (!result.canceled && result.assets[0].uri) {
                  handleImageSelected(result.assets[0].uri);
                }
                closeAlert();
              }}
              style={{
                backgroundColor: "orange",
                paddingVertical: 10,
                paddingHorizontal: 25,
                borderRadius: 8,
              }}
            >
              <Text
                style={{
                  fontSize: theme.typography.sizes.body1,
                  color: "white",
                  fontWeight: "bold",
                }}
              >
                Galería
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={() => closeAlert()}
              style={{
                backgroundColor: theme.colors.border,
                paddingVertical: 10,
                paddingHorizontal: 25,
                borderRadius: 8,
              }}
            >
              <Text
                style={{
                  fontSize: theme.typography.sizes.body1,
                  color: theme.colors.text,
                  fontWeight: "bold",
                }}
              >
                Cancelar
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      ),
    });
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
      <CustomisableAlert
        dismissable
        titleStyle={{
          fontSize: theme.typography.sizes.headline1,
          fontWeight: "bold",
        }}
        textStyle={{
          fontSize: theme.typography.sizes.body1,
        }}
        btnLabelStyle={{
          color: "white",
          paddingHorizontal: 10,
          textAlign: "center",
          fontSize: theme.typography.sizes.body1,
        }}
      />

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
            onPress={
              user?.profile?.profile_image
                ? handleImageOptions
                : showImageSourceOptions
            }
            activeOpacity={0.7}
          >
            {user?.profile?.profile_image ? (
              <>
                <Image
                  key={user?.profile?.profile_image}
                  source={{
                    uri: user?.profile?.profile_image,
                    cache: "reload",
                  }}
                  style={styles.existingImage}
                  onError={(e) =>
                    console.log("Error loading image:", e.nativeEvent.error)
                  }
                />
                <View style={styles.editButton}>
                  <Ionicons
                    name="pencil"
                    size={theme.typography.sizes.body1}
                    color="black"
                  />
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
                size={theme.typography.sizes.headline1}
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
                size={theme.typography.sizes.headline1}
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

          <View
            style={[
              styles.infoCard,
              { backgroundColor: theme.colors.card, marginBottom: 20 },
            ]}
          >
            <View style={styles.cardHeader}>
              <Ionicons
                name="help-circle-outline"
                size={theme.typography.sizes.headline1}
                color={theme.colors.text}
              />
              <Text style={[styles.cardTitle, { color: theme.colors.text }]}>
                Ayuda y Soporte
              </Text>
            </View>
            <Text style={[styles.value, { color: theme.colors.text }]}>
              Si tiene inconvenientes con la aplicación, comuníquese por{" "}
              <Text
                style={{ color: "blue" }}
                onPress={() => Linking.openURL("tel:+56977547545")}
              >
                llamada
              </Text>{" "}
              o{" "}
              <Text
                style={{ color: "blue" }}
                onPress={() => Linking.openURL("https://wa.me/56977547545")}
              >
                WhatsApp
              </Text>
              , de lunes a viernes entre 8:00 y 17:00 hrs., al siguiente número:{" "}
              <Text
                style={{ textDecorationLine: "underline" }}
                onPress={() => Linking.openURL("https://wa.me/56977547545")}
              >
                +56 9 7754 7545
              </Text>
            </Text>

            <View style={{ height: 15 }} />

            <Text style={[styles.value, { color: theme.colors.text }]}>
              En caso de no obtener respuesta oportuna, o tener una emergencia
              relacionada al estudio, comuníquese al correo:{" "}
              <Text
                style={{ textDecorationLine: "underline", color: "blue" }}
                onPress={() =>
                  Linking.openURL("mailto:fondef.caidas@gmail.com")
                }
              >
                fondef.caidas@gmail.com
              </Text>
            </Text>
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
    // flex: 1,
    paddingTop: 20,
    paddingBottom: 10,
  },
  profileImageSection: {
    alignItems: "center",
    marginBottom: 30,
  },
  imageContainer: {
    width: theme.typography.sizes.imageThumbnail,
    height: theme.typography.sizes.imageThumbnail,
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
    fontSize: theme.typography.sizes.headline1,
    fontWeight: "bold",
    marginBottom: 5,
  },
  email: {
    fontSize: theme.typography.sizes.body1,
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
    fontSize: theme.typography.sizes.subtitle,
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
    fontSize: theme.typography.sizes.body1,
    opacity: 0.8,
  },
  value: {
    fontSize: theme.typography.sizes.body1,
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
