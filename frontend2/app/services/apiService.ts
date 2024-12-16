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

  constructor() {
    this.baseUrl = API_URL;
    this.prevcadPrefix = '/prevcad';
  }

  public async getHeaders(includeAuth: boolean = true): Promise<HeadersInit> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (includeAuth) {
      const token = await AsyncStorage.getItem('auth_token');
      if (token) {
        // Validar token
        const isValid = await authService.validateToken(token);
        if (!isValid) {
          // Intentar refrescar el token
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
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    return headers;
  }

  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    if (response.status === 401) {
      // Token expirado o inválido
      const refreshToken = await AsyncStorage.getItem('refresh_token');
      if (refreshToken) {
        const newToken = await authService.refreshToken(refreshToken);
        if (newToken) {
          // Reintentar la petición original con el nuevo token
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

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || `API error: ${response.status}`);
    }

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
        this.getUrl('/user/profile'),
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

    uploadProfileImage: async (uri: string): Promise<ApiResponse<UserProfile>> => {
      const formData = new FormData();
      const filename = uri.split('/').pop() || 'image';
      const match = /\.(\w+)$/.exec(filename);
      const type = match ? `image/${match[1]}` : 'image';

      formData.append('profile_image', {
        uri,
        name: filename,
        type,
      } as any);

      const response = await fetch(
        this.getUrl('/user/profile/upload_image'),
        {
          method: 'POST',
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          body: formData as any,
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
          this.getUrl('/text_recommendations'),
          {
            headers: await this.getHeaders(),
          }
        );
        return this.handleResponse(response);
      } catch (error) {
        console.error('Error fetching recommendations:', error);
        throw error;
      }
    }
  };
}

export const apiService = new ApiClient();
export default apiService; 