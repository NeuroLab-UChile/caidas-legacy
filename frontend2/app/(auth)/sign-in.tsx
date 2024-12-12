import { useState } from 'react';
import { View, TextInput, Button, StyleSheet } from 'react-native';
import { useAuth } from '../contexts/auth';
import { router } from 'expo-router';

export default function SignIn() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { signIn } = useAuth();

  const handleLogin = async () => {
    try {
      await signIn(username, password);
      router.replace('/(tabs)');
    } catch (error) {
      // Manejar el error (mostrar un mensaje, etc.)
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
      <TextInput
        placeholder="Usuario"
        value={username}
        onChangeText={handleChangeUsername}
        style={styles.input}
      />
      <TextInput
        placeholder="Contraseña"
        value={password}
        onChangeText={handleChangePassword}
        secureTextEntry
        style={styles.input}
      />
      <Button title="Iniciar Sesión" onPress={handleLogin} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    padding: 10,
    marginBottom: 10,
    borderRadius: 5,
  },
});
