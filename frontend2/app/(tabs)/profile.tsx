import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  Image,
  ScrollView,
} from "react-native";
import apiService, { UserProfile } from "../services/apiService";
import { theme } from "@/src/theme";

const ProfileScreen = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const response = await apiService.user.getProfile();
      console.log("Respuesta completa:", response);
      console.log("Datos del perfil:", response.data);
      console.log("Tipo de datos:", typeof response.data);
      console.log(
        "Estructura de datos:",
        JSON.stringify(response.data, null, 2)
      );

      setProfile(response.data as UserProfile);
    } catch (err) {
      console.error("Error detallado:", err);
      setError("Error al cargar el perfil");
    } finally {
      setLoading(false);
    }
  };

  const getProfilePicture = () => {
    if (profile?.profile?.profile_picture) {
      let base64Image = profile.profile.profile_picture;

      // Verifica si la cadena tiene el prefijo de base64
      if (base64Image.startsWith("data:image")) {
        base64Image = base64Image.split(",").pop() || "";
      }

      return { uri: `data:image/jpeg;base64,${base64Image}` };
    }
    return null;
  };

  const InfoField = ({ label, value }: { label: string; value: string }) => (
    <View style={styles.infoField}>
      <Text style={styles.value}>{value}</Text>
      <Text style={styles.label}>{label}</Text>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>{error}</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {profile && (
        <View style={styles.content}>
          <View style={styles.avatarContainer}>
            {getProfilePicture() ? (
              <Image source={getProfilePicture()!} style={styles.avatar} />
            ) : (
              <View style={[styles.avatar, styles.avatarPlaceholder]}>
                <Text style={styles.avatarText}>
                  {profile.username.charAt(0).toUpperCase()}
                </Text>
              </View>
            )}
            <Text style={styles.editText}>EDITAR IMAGEN</Text>
          </View>

          <InfoField label="Nombre de usuario" value={profile.username} />
          <InfoField label="Correo electrónico" value={profile.email} />
          <InfoField
            label="Nombre y Apellido"
            value={`${profile.first_name} ${profile.last_name}`.trim()}
          />
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  content: {
    padding: theme.spacing.lg,
  },
  avatarContainer: {
    alignItems: "center",
    marginBottom: theme.spacing.xl,
  },
  avatar: {
    width: 100,
    height: 100,
    borderRadius: 50,
  },
  avatarPlaceholder: {
    backgroundColor: theme.colors.card,
    justifyContent: "center",
    alignItems: "center",
  },
  avatarText: {
    fontSize: 40,
    color: theme.colors.text,
  },
  editText: {
    marginTop: theme.spacing.sm,
    fontSize: 16,
    color: theme.colors.text + "80",
    fontWeight: "400",
  },
  infoField: {
    marginBottom: theme.spacing.lg,
  },
  label: {
    fontSize: 14,
    color: theme.colors.text + "80",
    marginTop: theme.spacing.xs,
  },
  value: {
    fontSize: 18,
    fontWeight: "bold",
    color: theme.colors.text,
  },
  errorText: {
    color: theme.colors.background,
    textAlign: "center",
    fontSize: theme.typography.sizes.labelLarge,
    fontFamily: theme.typography.primary.fontFamily,
  },
});

export default ProfileScreen;
