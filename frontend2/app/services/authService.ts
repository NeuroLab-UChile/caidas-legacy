import { API_URL } from '@/constants';
import AsyncStorage from '@react-native-async-storage/async-storage';

export interface AuthResponse {
  user: {
    id: number;
    username: string;
    email: string;
  };
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      console.log("Attempting login with:", credentials.username); // Debug

      const response = await fetch(`${API_URL}/token/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        throw new Error('Error en la autenticación');
      }

      const data = await response.json();
      console.log("Login successful, got token"); // Debug

      return data;
    } catch (error) {
      console.error('Error en login:', error);
      throw error;
    }
  },

  async getUserInfo(token: string) {
    try {
      const response = await fetch(`${API_URL}/prevcad/user/profile/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Error obteniendo información del usuario');
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting user info:', error);
      throw error;
    }
  },

  async validateToken(token: string): Promise<boolean> {
    try {
      const response = await fetch(`${API_URL}/token/verify/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      });
      return response.ok;
    } catch {
      return false;
    }
  },

  async refreshToken(refreshToken: string): Promise<string | null> {
    try {
      const response = await fetch(`${API_URL}/token/refresh/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh: refreshToken }),
      });

      if (!response.ok) throw new Error('No se pudo refrescar el token');

      const data = await response.json();
      await AsyncStorage.setItem('auth_token', data.access);
      return data.access;
    } catch (error) {
      console.error('Error refreshing token:', error);
      return null;
    }
  },

  async logout(): Promise<void> {
    try {
      await AsyncStorage.removeItem('auth_token');
      await AsyncStorage.removeItem('refresh_token');
    } catch (error) {
      console.error('Error during logout:', error);
      throw error;
    }
  },
};

export default authService; 