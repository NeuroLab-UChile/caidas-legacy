import AsyncStorage from '@react-native-async-storage/async-storage';

import authService from './authService';
import { API_URL } from '@/constants';

interface ApiResponse<T> {
  data: T;
  status: number;
}

export interface UserProfile {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  profile: {
    profile_picture?: string;
    [key: string]: any;  // Para otros campos dinámicos del perfil
  };
}

const apiService = {
  async request<T>(
    endpoint: string,
    options: RequestInit = {},
    usePrevcadPrefix: boolean = true
  ): Promise<ApiResponse<T>> {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      const refreshToken = await AsyncStorage.getItem('refresh_token');

      const headers = {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      };

      const baseUrl = usePrevcadPrefix ? `${API_URL}/prevcad` : API_URL;
      let response = await fetch(`${baseUrl}${endpoint}`, {
        ...options,
        headers,
      });

      console.log('URL completa:', `${baseUrl}${endpoint}`);
      console.log('Headers:', headers);

      // Si el token expiró, intentamos refrescarlo
      if (response.status === 401 && refreshToken) {
        const newToken = await authService.refreshToken(refreshToken);
        if (newToken) {
          headers.Authorization = `Bearer ${newToken}`;
          response = await fetch(`${baseUrl}${endpoint}`, {
            ...options,
            headers,
          });
        }
      }

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Respuesta de la API:', data);
      return { data, status: response.status };
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  },

  // Métodos específicos para diferentes endpoints
  categories: {
    async getAll() {
      return await apiService.request('/health_categories/');
    },

    async getById(id: number) {
      return await apiService.request(`/health_categories/${id}/`);
    },
  },

  textRecommendations: {
    async getAll() {
      return await apiService.request('/text_recommendations/');
    },
  },

  user: {
    async getProfile(): Promise<ApiResponse<UserProfile>> {
      return await apiService.request('/user/profile/');
    },

    async updateProfile(data: Partial<UserProfile>): Promise<ApiResponse<UserProfile>> {
      return await apiService.request('/user/profile/', {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    },
  },

  auth: {
    async login(credentials: { username: string; password: string }) {
      return await apiService.request('/token/', {
        method: 'POST',
        body: JSON.stringify(credentials),
      }, false); // No usar prefijo prevcad
    },

    async refreshToken(refreshToken: string) {
      return await apiService.request('/token/refresh/', {
        method: 'POST',
        body: JSON.stringify({ refresh: refreshToken }),
      }, false); // No usar prefijo prevcad
    },

    async validateToken(token: string) {
      return await apiService.request('/token/verify/', {
        method: 'POST',
        body: JSON.stringify({ token }),
      }, false); // No usar prefijo prevcad
    },
  },
};

export default apiService; 