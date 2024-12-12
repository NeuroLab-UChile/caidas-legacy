const API_URL = 'http://127.0.0.1:8000/api';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface TokenResponse {
  access: string;
  refresh: string;

}

export interface AuthResponse {
  user: {
    id: number;
    username: string;
    email: string;
  };
}

export const authService = {
  async login(credentials: LoginCredentials): Promise<TokenResponse> {
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

    return response.json();
  },

  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    const response = await fetch(`${API_URL}/token/refresh/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!response.ok) {
      throw new Error('Error al refrescar el token');
    }

    return response.json();
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

  isTokenExpired(token: string): boolean {
    try {
      const [, payload] = token.split('.');
      const decodedPayload = JSON.parse(atob(payload));
      const exp = decodedPayload.exp * 1000; // Convertir a milisegundos
      return Date.now() >= exp;
    } catch {
      return true;
    }
  },

  async checkProtectedEndpoint(token: string): Promise<boolean> {
    try {
      const response = await fetch(`${API_URL}/prevcad`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      return response.ok;
    } catch {
      return false;
    }
  }
};


export default authService