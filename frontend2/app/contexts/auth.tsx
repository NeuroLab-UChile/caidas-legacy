import React, { createContext, useContext, useState, useEffect } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import authService, { AuthResponse } from "../services/authService";
import { UserProfile } from "../services/apiService";

type AuthContextType = {
  token: string | null;
  isAuthenticated: boolean; // Nueva variable global
  signIn: (username: string, password: string) => Promise<boolean>;
  signOut: () => Promise<void>;
  isLoading: boolean;
  userProfile: UserProfile | null;
};

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    checkAuthState();
  }, []);

  const checkAuthState = async () => {
    try {
      const savedToken = await AsyncStorage.getItem("auth_token");
      if (savedToken) {
        const isValid = await authService.validateToken(savedToken);
        if (isValid) {
          setToken(savedToken);
        } else {
          await AsyncStorage.removeItem("auth_token");
        }
      }
    } catch (error) {
      console.error("Error checking auth state:", error);
      await AsyncStorage.removeItem("auth_token");
    } finally {
      setIsLoading(false);
    }
  };

  const signIn = async (
    username: string,
    password: string
  ): Promise<boolean> => {
    try {
      const response = await authService.login({ username, password });

      if (!response || !response.access) {
        console.log("No se recibió token de acceso");
        setIsAuthenticated(false);
        return false;
      }

      console.log("Token recibido:", response.access);
      setToken(response.access);
      await AsyncStorage.setItem("auth_token", response.access);

      if (response.refresh) {
        await AsyncStorage.setItem("refresh_token", response.refresh);
      }

      try {
        console.log("Intentando obtener perfil con token:", response.access);
        const profile = await authService.getUserInfo(response.access);
        if (profile) {
          console.log("Perfil obtenido:", profile);
          setUserProfile(profile);
          setIsAuthenticated(true);
          return true;
        }
      } catch (profileError) {
        console.error("Error obteniendo perfil:", profileError);
        await signOut();
        return false;
      }

      return false;
    } catch (error) {
      console.error("Error en signIn:", error);
      setIsAuthenticated(false);
      return false;
    }
  };

  const signOut = async () => {
    try {
      await AsyncStorage.removeItem("auth_token");
      await AsyncStorage.removeItem("refresh_token");
    } catch (error) {
      console.error("Error durante signOut:", error);
    } finally {
      setToken(null);
      setUserProfile(null);
      setIsAuthenticated(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        isAuthenticated,
        signIn: (username: string, password: string) =>
          signIn(username, password).then((result) => result),
        signOut,
        isLoading,
        userProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export default AuthProvider;
