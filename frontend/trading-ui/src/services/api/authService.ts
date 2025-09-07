import axios, { AxiosResponse } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8002';

interface LoginCredentials {
  username: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token: string;
  user: {
    id: string;
    username: string;
    email: string;
    firstName: string;
    lastName: string;
    role: string;
    accountId: string;
  };
}

interface RefreshTokenResponse {
  access_token: string;
  expires_in: number;
}

class AuthService {
  private api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response: AxiosResponse<LoginResponse> = await this.api.post('/auth/login', credentials);
    return response.data;
  }

  async refreshToken(refreshToken: string): Promise<RefreshTokenResponse> {
    const response: AxiosResponse<RefreshTokenResponse> = await this.api.post('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  }

  async logout(): Promise<void> {
    const token = localStorage.getItem('vedhavriddhi_token');
    if (token) {
      try {
        await this.api.post('/auth/logout', {}, {
          headers: { Authorization: `Bearer ${token}` },
        });
      } catch (error) {
        // Logout anyway, even if server request fails
        console.warn('Logout request failed:', error);
      }
    }
  }

  async validateToken(token: string): Promise<boolean> {
    try {
      const response = await this.api.get('/auth/validate', {
        headers: { Authorization: `Bearer ${token}` },
      });
      return response.status === 200;
    } catch {
      return false;
    }
  }

  async getUserProfile(): Promise<LoginResponse['user']> {
    const token = localStorage.getItem('vedhavriddhi_token');
    const response = await this.api.get('/auth/profile', {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  }
}

export const authService = new AuthService();
