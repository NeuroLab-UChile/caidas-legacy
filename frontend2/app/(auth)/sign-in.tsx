import { useState } from "react";
import { View, TextInput, Pressable, Text, StyleSheet, ActivityIndicator, Alert } from "react-native";
import Constants from 'expo-constants';

import { router } from "expo-router";
import { theme } from "@/src/theme";
import { useAuth } from "../contexts/auth";

export default function SignIn() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const { signIn } = useAuth();

  const handleLogin = async () => {
    if (!username || !password) {
      setError("Por favor ingresa usuario y contraseña");
      return;
    }

    try {
      setIsLoading(true);
      setError("");
      console.log('Intentando login con:', username);
      
      const success = await signIn(username, password);
      
      if (success) {
        console.log('Login exitoso, redirigiendo...');
        router.replace("/(tabs)/action/");
      } else {
        setError("Credenciales incorrectas");
      }
    } catch (error) {
      console.error('Error en login:', error);
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

  return (
    <View style={styles.container}>
      <Text style={styles.versionText}>
        Versión: {Constants.expoConfig?.version || '1.0.0'}
        {__DEV__ ? ' (Debug)' : ' (Release)'}
      </Text>

      <Text style={styles.title}>Iniciar Sesión</Text>

      {error ? <Text style={styles.errorText}>{error}</Text> : null}

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

      <Pressable
        style={({ pressed }) => [
          styles.button,
          pressed && styles.buttonPressed,
          isLoading && styles.buttonDisabled
        ]}
        onPress={handleLogin}
        disabled={isLoading}
      >
        {isLoading ? (
          <ActivityIndicator color={theme.colors.text} />
        ) : (
          <Text style={styles.buttonText}>Iniciar Sesión</Text>
        )}
      </Pressable>

      <Text style={styles.serverStatus}>
        Servidor: {isLoading ? 'Conectando...' : 'Listo'}
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
    color: 'red',
    marginBottom: theme.spacing.md,
    textAlign: 'center',
    fontFamily: theme.typography.fonts.primary.regular,
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  serverStatus: {
    marginTop: theme.spacing.xl,
    textAlign: 'center',
    color: theme.colors.text + '80',
    fontSize: theme.typography.sizes.caption,
  },
  versionText: {
    position: 'absolute',
    top: 40,
    right: 20,
    fontSize: 12,
    color: theme.colors.text + '80',
  },
});
