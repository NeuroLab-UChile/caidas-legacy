import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_URL } from '@/constants';
import authService from './authService';
import { Category } from '../types/category';
import { Platform } from 'react-native';
import * as FileSystem from 'expo-file-system';

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

interface ImageQuestionResponse {
  type: 'IMAGE_QUESTION';
  answer: string[];
}

interface ResponseData {
  [key: string]: ImageQuestionResponse | any;
}

// API Client Class
export class ApiClient {
  private baseUrl: string;
  private prevcadPrefix: string;
  private lastTokenValidation: number = 0;
  private tokenValidationInterval: number = 300000; // 5 minutos
  private tokenRefreshThreshold: number = 60000; // 1 minuto antes de expirar

  constructor() {
    this.baseUrl = API_URL;
    this.prevcadPrefix = '/prevcad';
    this.initializeTokenRefresh();
  }

  private async initializeTokenRefresh() {
    // Verificar token al iniciar
    await this.validateAndRefreshToken();

    // Configurar intervalo de verificación
    setInterval(async () => {
      await this.validateAndRefreshToken();
    }, this.tokenValidationInterval);
  }

  private async validateAndRefreshToken(): Promise<boolean> {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      if (!token) return false;

      const tokenData = this.parseJwt(token);
      if (!tokenData) return false;

      // Verificar si el token expirará pronto
      const expirationTime = tokenData.exp * 1000; // Convertir a milisegundos
      const currentTime = Date.now();

      if (expirationTime - currentTime < this.tokenRefreshThreshold) {
        const refreshToken = await AsyncStorage.getItem('refresh_token');
        if (!refreshToken) return false;

        const newToken = await authService.refreshToken(refreshToken);
        return !!newToken;
      }

      return true;
    } catch (error) {
      console.error('Error validating token:', error);
      return false;
    }
  }

  private parseJwt(token: string) {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(c =>
        '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
      ).join(''));
      return JSON.parse(jsonPayload);
    } catch (error) {
      console.error('Error parsing JWT:', error);
      return null;
    }
  }

  public async getHeaders(includeAuth: boolean = true): Promise<HeadersInit> {
    const headers: HeadersInit = {
      credentials: 'include',
    };

    if (includeAuth) {
      const token = await AsyncStorage.getItem('auth_token');
      if (!token) {
        throw new Error('No auth token found');
      }

      // Solo validar si es necesario
      if (Date.now() - this.lastTokenValidation > this.tokenValidationInterval) {
        const isValid = await this.validateAndRefreshToken();
        if (!isValid) {
          await authService.logout();
          throw new Error('Session expired');
        }
        this.lastTokenValidation = Date.now();
      }

      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }


  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    if (response.status === 401) {
      const token = await AsyncStorage.getItem('auth_token');
      const refreshToken = await AsyncStorage.getItem('refresh_token');

      if (token && refreshToken) {
        // Intentar validar el token actual primero
        const isValid = await authService.validateToken(token);
        if (!isValid) {
          // Si no es válido, intentar refrescar
          const newToken = await authService.refreshToken(refreshToken);
          if (newToken) {
            // Reintentar la petición original con el nuevo token
            const newResponse = await fetch(response.url, {
              ...response,
              headers: {
                ...response.headers,
                'Authorization': `Bearer ${newToken}`,
                credentials: 'include',
              }
            });
            return this.handleResponse(newResponse);
          }
        }
      }

      // Si no se pudo recuperar la sesión, hacer logout
      await authService.logout();
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
          headers: await this.getHeaders(true),
          body: JSON.stringify({ template_id: templateId }),
        }
      );
      return this.handleResponse<Category>(response);
    },

    saveResponses: async (categoryId: number, formData: FormData): Promise<ApiResponse<any>> => {
      try {
        const response = await fetch(
          this.getUrl(`/health-categories/${categoryId}/responses/`),
          {
            method: 'POST',
            body: formData,
            headers: await this.getHeaders(true),
          });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
      } catch (error) {
        console.error('Error in saveResponses:', error);
        throw error;
      }
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
            headers: await this.getHeaders(true),
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
          headers: await this.getHeaders(true),
        }
      );
      return this.handleResponse<Category>(response);
    },


  };


  // User Management
  public user = {
    getProfile: async (): Promise<ApiResponse<UserProfile>> => {
      try {
        const token = await AsyncStorage.getItem('auth_token');
        if (!token) {
          throw new Error('No auth token found');
        }

        const response = await fetch(
          this.getUrl('/user/profile/'),
          {
            headers: await this.getHeaders(),
          }
        );

        if (!response.ok) {
          const errorText = await response.text();
          console.error('Profile Error Response:', {
            status: response.status,
            statusText: response.statusText,
            body: errorText
          });
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return {
          data,
          status: response.status,
          message: data.message,
        };
      } catch (error) {
        console.error('Error fetching profile:', error);
        throw error;
      }
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

    uploadProfileImage: async (base64Image: string): Promise<ApiResponse<UserProfile>> => {
      try {
        const formData = new FormData();
        formData.append('image', base64Image);

        const token = await AsyncStorage.getItem('auth_token');
        if (!token) {
          throw new Error('No auth token found');
        }

        const response = await fetch(
          this.getUrl('/user/profile/upload_image/'),
          {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Accept': 'application/json',
            },
            body: formData,
          }
        );

        if (!response.ok) {
          const errorData = await response.json();
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

  private async createFormDataWithImages(responses: ResponseData, imageResponses: Record<string, string[]>) {
    // Convertir las respuestas normales y las imágenes en un solo objeto
    const allResponses = { ...responses };

    // Procesar cada pregunta con imágenes
    for (const [nodeId, imageUris] of Object.entries(imageResponses)) {
        try {
            const base64Images = await Promise.all(
                imageUris.map(async (uri) => {
                    const base64 = await FileSystem.readAsStringAsync(uri, {
                        encoding: FileSystem.EncodingType.Base64,
                    });
                    return `data:image/jpeg;base64,${base64}`;
                })
            );

            // Añadir las imágenes en base64 a las respuestas
            allResponses[nodeId] = {
                type: 'IMAGE_QUESTION',
                answer: {
                    images: base64Images
                }
            };
        } catch (error) {
            console.error(`Error procesando imágenes para nodeId ${nodeId}:`, error);
        }
    }

    return JSON.stringify(allResponses);
  }

  public evaluations = {
    saveResponses: async (categoryId: number, responses: ResponseData): Promise<ApiResponse<any>> => {
        try {
            const processedResponses = await this.createFormDataWithImages(responses, {});
            
            const response = await fetch(
                this.getUrl(`/health_categories/${categoryId}/responses/`),
                {
                    method: 'POST',
                    headers: {
                        ...(await this.getHeaders()),
                        'Content-Type': 'application/json',
                    },
                    body: processedResponses,
                }
            );

            if (!response.ok) {
                throw new Error('Error saving responses');
            }

            return this.handleResponse(response);
        } catch (error) {
            console.error('Error in saveResponses:', error);
            throw error;
        }
    },

    clearAndStartNew: async (categoryId: number): Promise<ApiResponse<any>> => {
        try {
            console.log('Iniciando nueva evaluación para categoría:', categoryId);
            
            const response = await fetch(
                this.getUrl(`/health_categories/${categoryId}/clear_evaluation/`),
                {
                    method: 'POST',
                    headers: await this.getHeaders(),
                }
            );

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return this.handleResponse(response);
        } catch (error) {
            console.error('Error al iniciar nueva evaluación:', error);
            throw error;
        }
    },
  };
}

export const apiService = new ApiClient();
export default apiService; 