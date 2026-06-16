import { TouchableOpacity, StyleSheet, View, Text, Alert } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import * as ImagePicker from "expo-image-picker";
import { theme } from "@/src/theme";
import CustomisableAlert, {
  showAlert,
  closeAlert,
} from "react-native-customisable-alert";

interface ImageUploaderProps {
  onImageSelected: (base64Image: string) => void;
}

export function ImageUploader({ onImageSelected }: ImageUploaderProps) {
  const showImageSourceOptions = async () => {
    // Alert.alert("Seleccionar foto", "¿De dónde quieres seleccionar la foto?", [
    //   {
    //     text: "Cámara",
    //     onPress: async () => {
    //       const { status } = await ImagePicker.requestCameraPermissionsAsync();
    //       if (status !== "granted") {
    //         // Alert.alert("Se necesita permiso para acceder a la cámara");
    //         showAlert({
    //           title: "Error",
    //           btnLabel: "OK",
    //           message: "Se necesita permiso para acceder a la cámara",
    //           alertType: "error",
    //         });
    //         return;
    //       }

    //       const result = await ImagePicker.launchCameraAsync({
    //         allowsEditing: true,
    //         aspect: [1, 1],
    //         quality: 0.5,
    //         base64: true,
    //       });

    //       if (!result.canceled && result.assets[0]) {
    //         const base64Image = `data:image/jpeg;base64,${result.assets[0].base64}`;
    //         onImageSelected(base64Image);
    //       }
    //     },
    //   },
    //   {
    //     text: "Galería",
    //     onPress: async () => {
    //       const { status } =
    //         await ImagePicker.requestMediaLibraryPermissionsAsync();
    //       if (status !== "granted") {
    //         // Alert.alert("Se necesita permiso para acceder a la galería");
    //         showAlert({
    //           title: "Error",
    //           btnLabel: "OK",
    //           message: "Se necesita permiso para acceder a la galería",
    //           alertType: "error",
    //         });
    //         return;
    //       }

    //       const result = await ImagePicker.launchImageLibraryAsync({
    //         mediaTypes: ImagePicker.MediaTypeOptions.Images,
    //         allowsEditing: true,
    //         aspect: [1, 1],
    //         quality: 0.5,
    //         base64: true,
    //       });

    //       if (!result.canceled && result.assets[0]) {
    //         const base64Image = `data:image/jpeg;base64,${result.assets[0].base64}`;
    //         onImageSelected(base64Image);
    //       }
    //     },
    //   },
    //   {
    //     text: "Cancelar",
    //     style: "cancel",
    //   },
    // ]);

    showAlert({
      title: "Seleccionar foto",
      message: "De dónde quieres seleccionar la foto?",
      alertType: "custom",
      customAlert: (
        <View>
          <View
            style={{
              backgroundColor: "white",
              padding: 20,
              width: "85%",
              height: "80%",
              borderRadius: 10,
              flexDirection: "column",
            }}
          >
            <Text
              style={{
                textAlign: "center",
                fontSize: theme.typography.sizes.headline1,
                fontWeight: "bold",
                marginBottom: 20,
              }}
            >
              Seleccionar foto
            </Text>
            <Text
              style={{
                fontSize: theme.typography.sizes.body2,
                color: theme.colors.text,
                marginBottom: 20,
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
                    // Alert.alert("Se necesita permiso para acceder a la cámara");
                    showAlert({
                      title: "Error",
                      btnLabel: "OK",
                      message: "Se necesita permiso para acceder a la cámara",
                      alertType: "error",
                    });
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
                  closeAlert();
                }}
                style={{
                  backgroundColor: "green",
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
                    // Alert.alert("Se necesita permiso para acceder a la galería");
                    showAlert({
                      title: "Error",
                      btnLabel: "OK",
                      message: "Se necesita permiso para acceder a la galería",
                      alertType: "error",
                    });
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
                  Galería
                </Text>
              </TouchableOpacity>

              <TouchableOpacity
                onPress={() => {
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
                  Cancelar
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      ),
    });
  };

  return (
    <>
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
      <TouchableOpacity onPress={showImageSourceOptions}>
        <Ionicons name="camera" size={40} color={theme.colors.text} />
      </TouchableOpacity>
    </>
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
    fontSize: theme.typography.sizes.body1,
    fontWeight: "500",
  },
});
