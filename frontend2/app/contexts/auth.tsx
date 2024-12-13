import { createContext, useContext, useState, useEffect } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import authService, { AuthResponse } from "../services/authService";

type AuthContextType = {
  user: AuthResponse["user"] | null;
  token: string | null;
  signIn: (username: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  isLoading: boolean;
};

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<AuthResponse["user"] | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuthState();
  }, []);

  const checkAuthState = async () => {
    try {
      const savedToken = await AsyncStorage.getItem("auth_token");
      if (savedToken) {
        const authResponse = await authService.validateToken(savedToken);

        setToken(savedToken);
      }
    } catch (error) {
      // Token inválido o expirado
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
    } catch (error) {
      throw new Error("Error al iniciar sesión");
    }
  };

  const signOut = async () => {
    try {
      // Eliminar tokens
      await AsyncStorage.removeItem("access_token");
      await AsyncStorage.removeItem("refresh_token");
      await AsyncStorage.removeItem("user_data"); // si guardas datos del usuario

      // Limpiar estado
      setToken(null);
      setUser(null);
      setIsAuthenticated(false);

      // Opcional: Invalidar token en el backend
      const currentToken = await AsyncStorage.getItem("access_token");
      if (currentToken) {
        try {
          await fetch(`${process.env.BASE_URL}/logout/`, {
            method: "POST",
            headers: {
              Authorization: `Bearer ${currentToken}`,
              "Content-Type": "application/json",
            },
          });
        } catch (error) {
          console.log("Error al invalidar token en backend:", error);
        }
      }
    } catch (error) {
      console.error("Error durante el logout:", error);
      throw new Error("Error al cerrar sesión");
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, signIn, signOut, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
};
function setIsAuthenticated(arg0: boolean) {
  throw new Error("Function not implemented.");
}
