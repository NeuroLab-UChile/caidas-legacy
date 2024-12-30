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
      const response = await fetch(`${API_URL}/token/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      const data = await response.json();

      if (!response.ok) {
        console.error("Error de autenticación:", data);
        throw new Error(data.detail || 'Error en la autenticación');
      }

      if (!data.access) {
        throw new Error('Token de acceso no recibido');
      }

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
        const errorData = await response.json();
        console.error("Error obteniendo perfil:", errorData);
        throw new Error('Error obteniendo información del usuario');
      }

      const data = await response.json();
      return data;
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