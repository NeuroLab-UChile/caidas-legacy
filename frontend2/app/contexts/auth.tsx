import React, { createContext, useContext, useState, useEffect } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import authService, { AuthResponse } from "../services/authService";
import { UserProfile } from "../services/apiService";

type AuthContextType = {
  token: string | null;
  isAuthenticated: boolean; // Nueva variable global
  signIn: (username: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  isLoading: boolean;
  userProfile: UserProfile | null;
};

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);

  const isAuthenticated = !!token; // Nueva lógica para determinar autenticación

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

  const signIn = async (username: string, password: string) => {
    try {
      const response = await authService.login({ username, password });
      setToken(response.access);

      await AsyncStorage.setItem("auth_token", response.access);
      await AsyncStorage.setItem("refresh_token", response.refresh);

      const profile = await authService.getUserInfo(response.access);
      setUserProfile(profile);

      return true;
    } catch (error) {
      console.error("Login failed:", error);
      return false;
    }
  };

  const signOut = async () => {
    await AsyncStorage.removeItem("auth_token");
    await AsyncStorage.removeItem("refresh_token");
    setToken(null);
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        isAuthenticated,
        signIn: (username: string, password: string) =>
          signIn(username, password).then(() => {}),
        signOut,
        isLoading,
        userProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
};
