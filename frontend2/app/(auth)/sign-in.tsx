import { useState } from "react";
import { View, TextInput, Pressable, Text, StyleSheet } from "react-native";

import { router } from "expo-router";
import { theme } from "@/src/theme";
import { useAuth } from "../contexts/auth";

export default function SignIn() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const { signIn } = useAuth();

  const handleLogin = async () => {
    try {
      const success = await signIn(username, password);
      if (success) {
        router.replace("/(tabs)/action/");
      }
    } catch (error) {
      console.error(error);
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
      <Text style={styles.title}>Iniciar Sesión</Text>

      <TextInput
        placeholder="Usuario"
        value={username}
        onChangeText={handleChangeUsername}
        style={styles.input}
        placeholderTextColor={theme.colors.text + "80"}
        autoCapitalize="none"
      />

      <TextInput
        placeholder="Contraseña"
        value={password}
        onChangeText={handleChangePassword}
        secureTextEntry
        style={styles.input}
        placeholderTextColor={theme.colors.text + "80"}
        autoCapitalize="none"
      />

      <Pressable
        style={({ pressed }) => [
          styles.button,
          pressed && styles.buttonPressed,
        ]}
        onPress={handleLogin}
      >
        <Text style={styles.buttonText}>Iniciar Sesión</Text>
      </Pressable>
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
});
