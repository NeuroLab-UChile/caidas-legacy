import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_URL } from '@/constants';
import authService from './authService';
import { Category } from '../types/category';

// Types
interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
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
    [key: string]: any;
  };
}



// API Client Class
class ApiClient {
  private baseUrl: string;
  private prevcadPrefix: string;
  private lastTokenValidation: number = 0;
  private tokenValidationInterval: number = 60000; // 1 minuto

  constructor() {
    this.baseUrl = API_URL;
    this.prevcadPrefix = '/prevcad';
  }

  private shouldValidateToken(): boolean {
    const now = Date.now();
    if (now - this.lastTokenValidation > this.tokenValidationInterval) {
      this.lastTokenValidation = now;
      return true;
    }
    return false;
  }

  public async getHeaders(includeAuth: boolean = true): Promise<HeadersInit> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (includeAuth) {
      const token = await AsyncStorage.getItem('auth_token');
      if (!token) {
        throw new Error('No auth token found');
      }

      // Solo validar el token si ha pasado el intervalo
      if (this.shouldValidateToken()) {
        const isValid = await authService.validateToken(token);
        if (!isValid) {
          const refreshToken = await AsyncStorage.getItem('refresh_token');
          if (refreshToken) {
            const newToken = await authService.refreshToken(refreshToken);
            if (newToken) {
              headers['Authorization'] = `Bearer ${newToken}`;
              return headers;
            }
          }
          throw new Error('Session expired');
        }
      }

      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }

  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    if (response.status === 401) {
      const refreshToken = await AsyncStorage.getItem('refresh_token');
      if (refreshToken) {
        const newToken = await authService.refreshToken(refreshToken);
        if (newToken) {
          const newResponse = await fetch(response.url, {
            ...response,
            headers: {
              ...response.headers,
              'Authorization': `Bearer ${newToken}`
            }
          });
          return this.handleResponse(newResponse);
        }
      }
      throw new Error('Session expired');
    }

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    return {
      data,
      status: response.status,
      message: data.message,
    };
  }

  private getUrl(endpoint: string, usePrevcadPrefix: boolean = true): string {
    return `${this.baseUrl}${usePrevcadPrefix ? this.prevcadPrefix : ''}${endpoint}`;
  }

  // Health Categories
  public categories = {
    create: async (templateId: number): Promise<ApiResponse<Category>> => {
      const response = await fetch(
        this.getUrl('/health-categories/create'),
        {
          method: 'POST',
          headers: await this.getHeaders(),
          body: JSON.stringify({ template_id: templateId }),
        }
      );
      return this.handleResponse<Category>(response);
    },

    saveResponses: async (categoryId: number, responses: any): Promise<ApiResponse<any>> => {
      const response = await fetch(
        this.getUrl(`/health-categories/${categoryId}/responses/`),
        {
          method: 'POST',
          headers: await this.getHeaders(),
          body: JSON.stringify({ responses }),
        }
      );
      return this.handleResponse(response);
    },

    getAll: async (): Promise<ApiResponse<Category[]>> => {
      try {
        const token = await AsyncStorage.getItem('auth_token');
        if (!token) {
          throw new Error('No auth token found');
        }

        const response = await fetch(
          this.getUrl('/health_categories/'),
          {
            headers: await this.getHeaders(),
          }
        );
        return this.handleResponse<Category[]>(response);
      } catch (error) {
        console.error('Error fetching categories:', error);
        throw error;
      }
    },

    getById: async (id: number): Promise<ApiResponse<Category>> => {
      const response = await fetch(
        this.getUrl(`/health_categories/${id}`),
        {
          headers: await this.getHeaders(),
        }
      );
      return this.handleResponse<Category>(response);
    },


  };


  // User Management
  public user = {
    getProfile: async (): Promise<ApiResponse<UserProfile>> => {
      const response = await fetch(
        this.getUrl('/user/profile/'),
        {
          headers: await this.getHeaders(),
        }
      );
      return this.handleResponse<UserProfile>(response);
    },

    updateProfile: async (data: Partial<UserProfile>): Promise<ApiResponse<UserProfile>> => {
      const response = await fetch(
        this.getUrl('/user/profile'),
        {
          method: 'PUT',
          headers: await this.getHeaders(),
          body: JSON.stringify(data),
        }
      );
      return this.handleResponse<UserProfile>(response);
    },

    uploadProfileImage: async (imageUri: string): Promise<ApiResponse<UserProfile>> => {
      try {
        console.log("Starting image upload...");

        const formData = new FormData();

        // Obtener el nombre del archivo y su extensión
        const filename = imageUri.split('/').pop() || 'profile-image.jpg';
        const match = /\.(\w+)$/.exec(filename);
        const type = match ? `image/${match[1]}` : 'image/jpeg';

        // Agregar la imagen al FormData con la estructura correcta
        formData.append('profile_image', {
          uri: imageUri,
          type,
          name: filename,
        } as any);

        const token = await AsyncStorage.getItem('auth_token');
        if (!token) {
          throw new Error('No auth token found');
        }

        // Usar la ruta específica para subir imágenes
        const response = await fetch(
          this.getUrl('/user/profile/upload_image/'),  // Ruta actualizada
          {
            method: 'POST',  // Cambiado a POST para coincidir con el backend
            headers: {
              'Authorization': `Bearer ${token}`,
              'Accept': 'application/json',
            },
            body: formData,
          }
        );

        console.log('Upload response status:', response.status);

        if (!response.ok) {
          const errorData = await response.json();
          console.error('Upload error:', errorData);
          throw new Error(errorData.detail || 'Error uploading image');
        }

        return this.handleResponse<UserProfile>(response);
      } catch (error) {
        console.error("Error uploading image:", error);
        throw error;
      }
    },

    deleteProfileImage: async (): Promise<ApiResponse<UserProfile>> => {
      const response = await fetch(
        this.getUrl('/user/profile/delete_image/'),
        {
          method: 'DELETE',
          headers: await this.getHeaders(),
        }
      );
      return this.handleResponse<UserProfile>(response);
    },
  };

  public recommendations = {
    getAll: async (): Promise<ApiResponse<any>> => {
      try {
        const token = await AsyncStorage.getItem('auth_token');
        if (!token) {
          throw new Error('No auth token found');
        }

        const response = await fetch(
          this.getUrl('/text_recommendations/'),
          {
            headers: await this.getHeaders(),
          }
        );
        return this.handleResponse(response);
      } catch (error) {
        console.error('Error fetching recommendations:', error);
        throw error;
      }
    },
    registerClick: async (recommendationId: number): Promise<ApiResponse<any>> => {
      const response = await fetch(
        this.getUrl(`/text_recommendations/${recommendationId}/register_click`),
        {
          method: 'POST',
          headers: {
            ...(await this.getHeaders()),
            'Accept': 'application/json',
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error Response:', {
          status: response.status,
          statusText: response.statusText,
          body: errorText
        });
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    }
  };

  public events = {
    getAll: async (): Promise<ApiResponse<any>> => {
      const response = await fetch(
        this.getUrl('/appointments/'),
        {
          headers: await this.getHeaders(),
        }
      );
      return this.handleResponse(response);
    }
  }
}

export const apiService = new ApiClient();
export default apiService; 