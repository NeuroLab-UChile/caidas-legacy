import { useState, useEffect } from "react";
import {
  View,
  TextInput,
  Pressable,
  Text,
  StyleSheet,
  ActivityIndicator,
  Alert,
} from "react-native";
import CheckBox from "expo-checkbox"; // https://docs.expo.dev/versions/latest/sdk/checkbox/
import Constants from "expo-constants";
import AsyncStorage from "@react-native-async-storage/async-storage";

import { router } from "expo-router";
import { theme } from "@/src/theme";
import { useAuth } from "../contexts/auth";
import { apiService } from "@/app/services/apiService";
import { termsAndConditions } from "@/constants/terms_and_conditions"; // Importar términos y condiciones

export default function SignIn() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [autoLoginMessage, setAutoLoginMessage] = useState("");
  const [acceptTerms, setAcceptTerms] = useState(false);
  const { signIn } = useAuth();

  // Detectar si hay usuario y contraseña guardados en el dispositivo e iniciar sesión automáticamente
  const autoLogin = async () => {
    const storedUsername = await AsyncStorage.getItem("username");
    const storedPassword = await AsyncStorage.getItem("password");

    if (storedUsername && storedPassword) {
      console.log("Iniciando sesión automáticamente con:", storedUsername);
      setUsername(storedUsername);
      setPassword(storedPassword);
      setRememberMe(true);
      setAcceptTerms(true); // Aceptar términos automáticamente si hay credenciales guardadas

      // Mostrar mensaje de auto-login y esperar 1 segundo antes de iniciar sesión
      setAutoLoginMessage("Iniciando sesión automáticamente...");
      setTimeout(() => {
        handleLogin(storedUsername, storedPassword, true);
      }, 2000); // Esperar para iniciar sesión automáticamente
    }
  };

  // Llamar a autoLogin al montar el componente
  useEffect(() => {
    autoLogin();
  }, []);

  const handleLogin = async (
    _username: string = "",
    _password: string = "",
    forcedAcceptTerms: boolean = false
  ) => {
    if (!acceptTerms && !forcedAcceptTerms) {
      setError("Debes aceptar los términos y condiciones para continuar.");
      return;
    }

    // Si no se pasan username y password, usar los del estado
    if (!_username) _username = username;
    if (!_password) _password = password;
    // Validar que se hayan ingresado usuario y contraseña
    if (!_username || !_password) {
      setError("Por favor ingresa usuario y contraseña");
      return;
    }

    try {
      setIsLoading(true);
      setError("");
      console.log("Intentando login con:", _username);

      const success = await signIn(_username, _password);

      if (success) {
        console.log("Login exitoso, redirigiendo...");
        // Guardar usuario y contraseña si rememberMe es true
        if (rememberMe) {
          await AsyncStorage.setItem("username", _username);
          await AsyncStorage.setItem("password", _password);
          console.log("Credenciales guardadas");
        }
        await apiService.activityLog.trackAction("login", 2); // Record action
        // Redirigir a la pantalla de acción
        router.replace("/(tabs)/action/");
      } else {
        setError("Credenciales incorrectas");
      }
    } catch (error) {
      console.error("Error en login:", error);
      setError("Error al iniciar sesión. Intenta nuevamente.");
      Alert.alert(
        "Error",
        "No se pudo conectar al servidor. Verifica tu conexión."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleChangeUsername = (text: string) => {
    setUsername(text.toLowerCase());
  };

  const handleChangePassword = (text: string) => {
    setPassword(text.toLowerCase());
  };

  const showTermsPopup = () => {
    Alert.alert("Términos y Condiciones", termsAndConditions, [
      { text: "Aceptar", onPress: () => setAcceptTerms(true) },
      { text: "Cancelar", onPress: () => setAcceptTerms(false) },
    ]);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.versionText}>
        Versión: {Constants.expoConfig?.version || "1.0.0"}
        {__DEV__ ? " (Debug)" : " (Release)"}
      </Text>

      <Text style={styles.title}>Iniciar Sesión</Text>

      {error ? <Text style={styles.errorText}>{error}</Text> : null}
      {autoLoginMessage ? (
        <Text style={styles.autoLoginMessage}>{autoLoginMessage}</Text>
      ) : null}

      <TextInput
        placeholder="Usuario"
        value={username}
        onChangeText={handleChangeUsername}
        style={styles.input}
        placeholderTextColor={theme.colors.text + "80"}
        autoCapitalize="none"
        editable={!isLoading}
      />

      <TextInput
        placeholder="Contraseña"
        value={password}
        onChangeText={handleChangePassword}
        secureTextEntry
        style={styles.input}
        placeholderTextColor={theme.colors.text + "80"}
        autoCapitalize="none"
        editable={!isLoading}
      />

      <View
        style={{
          flexDirection: "row",
          alignItems: "center",
          marginBottom: theme.spacing.md,
        }}
      >
        <CheckBox
          value={rememberMe}
          onValueChange={setRememberMe}
          disabled={isLoading}
          color={"black"}
        />
        <Text style={{ color: "black", marginLeft: 8 }}>Recordarme</Text>
      </View>

      {/* Link a popup y checkbox de Aceptar términos y condiciones */}
      <View
        style={{
          flexDirection: "row",
          alignItems: "center",
          marginBottom: theme.spacing.md,
        }}
      >
        <CheckBox
          value={acceptTerms}
          onValueChange={setAcceptTerms}
          disabled={isLoading}
          color={"black"}
        />
        <Text style={{ color: "black", marginLeft: 8 }}>
          Acepto los{" "}
          {/* términos y condiciones debe ser un link que active un popup */}
          <Text
            style={{
              color: "blue",
              fontWeight: "bold",
              textDecorationLine: "underline",
            }}
            onPress={showTermsPopup}
          >
            términos y condiciones
          </Text>
        </Text>
      </View>

      <Pressable
        style={({ pressed }) => [
          styles.button,
          pressed && styles.buttonPressed,
          (!acceptTerms || isLoading) && styles.buttonDisabled,
        ]}
        onPress={() => handleLogin()}
        disabled={isLoading}
      >
        {isLoading ? (
          <ActivityIndicator color={theme.colors.text} />
        ) : (
          <Text style={styles.buttonText}>Iniciar Sesión</Text>
        )}
      </Pressable>

      <Text style={styles.serverStatus}>
        Servidor: {isLoading ? "Conectando..." : "Listo"}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    padding: theme.spacing.xl,
    backgroundColor: theme.colors.background,
  },
  title: {
    fontSize: theme.typography.sizes.title,
    fontFamily: theme.typography.fonts.primary.bold,
    color: theme.colors.text,
    marginBottom: theme.spacing.xl,
    textAlign: "center",
  },
  input: {
    height: 50,
    borderWidth: theme.components.button.variants.primary.borderWidth,
    borderColor: theme.components.button.variants.primary.borderColor,
    borderRadius: theme.components.button.variants.primary.borderRadius,
    paddingHorizontal: theme.spacing.md,
    marginBottom: theme.spacing.md,
    fontSize: theme.typography.sizes.body1,
    fontFamily: theme.typography.fonts.primary.regular,
    color: theme.colors.text,
    backgroundColor: theme.colors.card,
  },
  button: {
    backgroundColor: theme.colors.primary,
    padding: theme.spacing.md,
    borderRadius: theme.components.button.variants.primary.borderRadius,
    alignItems: "center",
    marginTop: theme.spacing.md,
    borderWidth: theme.components.button.variants.primary.borderWidth,
    borderColor: theme.components.button.variants.primary.borderColor,
  },
  buttonPressed: {
    opacity: 0.8,
  },
  buttonText: {
    color: theme.colors.text,
    fontSize: theme.typography.sizes.body1,
    fontFamily: theme.typography.fonts.primary.bold,
  },
  errorText: {
    color: "red",
    marginBottom: theme.spacing.md,
    textAlign: "center",
    fontFamily: theme.typography.fonts.primary.regular,
  },
  autoLoginMessage: {
    color: "green",
    marginBottom: theme.spacing.md,
    textAlign: "center",
    fontFamily: theme.typography.fonts.primary.regular,
  },
  buttonDisabled: {
    opacity: 0.5,
    backgroundColor: theme.colors.disabled,
    borderColor: theme.colors.disabled,
  },
  serverStatus: {
    marginTop: theme.spacing.xl,
    textAlign: "center",
    color: theme.colors.text + "80",
    fontSize: theme.typography.sizes.caption,
  },
  versionText: {
    position: "absolute",
    top: 40,
    right: 20,
    fontSize: 12,
    color: theme.colors.text + "80",
  },
});
