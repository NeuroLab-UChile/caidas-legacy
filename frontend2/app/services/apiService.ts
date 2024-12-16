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
      console.log('🔑 Token usado:', token ? 'Presente' : 'Ausente');

      const headers = {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      };

      const baseUrl = usePrevcadPrefix ? `${API_URL}/prevcad` : API_URL;
      const fullUrl = `${baseUrl}${endpoint}`;
      console.log('🌐 Haciendo petición a:', fullUrl);
      console.log('📤 Headers:', headers);
      console.log('📦 Options:', options);

      let response = await fetch(fullUrl, {
        ...options,
        headers,
      });

      console.log('📥 Status:', response.status);
      const responseData = await response.json();
      console.log('📥 Response data:', responseData);

      // Si el token expiró, intentamos refrescarlo
      if (response.status === 401 && refreshToken) {
        console.log('🔄 Token expirado, intentando refrescar...');
        const newToken = await authService.refreshToken(refreshToken);
        if (newToken) {
          console.log('🔑 Token refrescado exitosamente');
          headers.Authorization = `Bearer ${newToken}`;
          response = await fetch(fullUrl, {
            ...options,
            headers,
          });
          console.log('📥 Nuevo status después de refrescar:', response.status);
        }
      }

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      return { data: responseData, status: response.status };
    } catch (error) {
      console.error('❌ API request failed:', error);
      throw error;
    }
  },

  // Métodos específicos para diferentes endpoints
  categories: {
    async getAll() {
      console.log('📋 Solicitando todas las categorías...');
      const result = await apiService.request('/health_categories/');
      console.log('📋 Categorías recibidas:', result.data);
      return result;
    },

    async getById(id: number) {
      console.log(`📋 Solicitando categoría ${id}...`);
      const result = await apiService.request(`/health_categories/${id}/`);
      console.log(`📋 Categoría ${id} recibida:`, result.data);
      return result;
    },
  },

  textRecommendations: {
    async getAll() {
      return await apiService.request('/text_recommendations/');
    },
  },

  user: {
    async getProfile(): Promise<ApiResponse<UserProfile>> {
      return await apiService.request('/user/profile/', {}, true);
    },

    async updateProfile(data: Partial<UserProfile>): Promise<ApiResponse<UserProfile>> {
      return await apiService.request('/user/profile/', {
        method: 'PUT',
        body: JSON.stringify(data),
      }, true);
    },

    async uploadProfileImage(uri: string): Promise<ApiResponse<UserProfile>> {
      console.log('1. Iniciando subida de imagen:', uri);

      const formData = new FormData();
      const filename = uri.split('/').pop();
      const match = /\.(\w+)$/.exec(filename || '');
      const type = match ? `image/${match[1]}` : 'image';

      console.log('2. Preparando datos de imagen:', { filename, type });

      formData.append('profile_image', {
        uri,
        name: filename,
        type,
      } as any);

      return await apiService.request('/user/profile/upload_image/', {
        method: 'POST',
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        body: formData as any,
      }, true);
    },

    deleteProfileImage: async () => {
      const response = await apiService.request('/users/profile/image/', {
        method: 'DELETE',
      }, true);
      return response;
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