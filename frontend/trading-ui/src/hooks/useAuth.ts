import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../store';
import { login, logout, refreshToken, setLoading } from '../store/slices/authSlice';
import { authService } from '../services/api/authService';

interface LoginCredentials {
  username: string;
  password: string;
}

interface User {
  id: string;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  role: string;
  accountId: string;
}

export const useAuth = () => {
  const dispatch = useDispatch();
  const { user, token, isAuthenticated, isLoading, error } = useSelector(
    (state: RootState) => state.auth
  );

  const [loginError, setLoginError] = useState<string | null>(null);

  useEffect(() => {
    // Check for existing token on app start
    const storedToken = localStorage.getItem('vedhavriddhi_token');
    const storedUser = localStorage.getItem('vedhavriddhi_user');

    if (storedToken && storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        dispatch(login({ user: parsedUser, token: storedToken }));
      } catch (error) {
        console.error('Failed to parse stored user data:', error);
        localStorage.removeItem('vedhavriddhi_token');
        localStorage.removeItem('vedhavriddhi_user');
      }
    }
  }, [dispatch]);

  const loginUser = async (credentials: LoginCredentials): Promise<boolean> => {
    setLoginError(null);
    dispatch(setLoading(true));

    try {
      const response = await authService.login(credentials);
      
      // Store in Redux
      dispatch(login({
        user: response.user,
        token: response.access_token,
      }));

      // Store in localStorage for persistence
      localStorage.setItem('vedhavriddhi_token', response.access_token);
      localStorage.setItem('vedhavriddhi_user', JSON.stringify(response.user));

      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Login failed';
      setLoginError(errorMessage);
      return false;
    } finally {
      dispatch(setLoading(false));
    }
  };

  const logoutUser = () => {
    dispatch(logout());
    localStorage.removeItem('vedhavriddhi_token');
    localStorage.removeItem('vedhavriddhi_user');
    localStorage.removeItem('vedhavriddhi_refresh_token');
  };

  const refreshUserToken = async (): Promise<boolean> => {
    const refreshTokenValue = localStorage.getItem('vedhavriddhi_refresh_token');
    
    if (!refreshTokenValue) {
      logoutUser();
      return false;
    }

    try {
      const response = await authService.refreshToken(refreshTokenValue);
      
      dispatch(refreshToken(response.access_token));
      localStorage.setItem('vedhavriddhi_token', response.access_token);
      
      return true;
    } catch (error) {
      logoutUser();
      return false;
    }
  };

  const checkTokenExpiry = () => {
    if (!token) return false;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      
      // Check if token expires in next 5 minutes
      if (payload.exp - currentTime < 300) {
        refreshUserToken();
        return false;
      }
      
      return payload.exp > currentTime;
    } catch {
      logoutUser();
      return false;
    }
  };

  const hasPermission = (resource: string, action: string): boolean => {
    if (!user || !isAuthenticated) return false;
    
    // Admin has all permissions
    if (user.role === 'administrator') return true;
    
    // Basic permission checks based on role
    const rolePermissions: Record<string, string[]> = {
      trader: ['orders.create', 'orders.read', 'trades.read', 'positions.read'],
      risk_manager: ['orders.read', 'trades.read', 'positions.read', 'risk.read', 'risk.manage'],
      compliance_officer: ['orders.read', 'trades.read', 'compliance.read', 'compliance.manage'],
      portfolio_manager: ['orders.read', 'trades.read', 'positions.read', 'portfolio.read', 'portfolio.manage'],
    };

    const userPermissions = rolePermissions[user.role] || [];
    const permission = `${resource}.${action}`;
    
    return userPermissions.includes(permission);
  };

  const isInRole = (role: string): boolean => {
    return user?.role === role;
  };

  return {
    user,
    token,
    isAuthenticated,
    isLoading,
    error: error || loginError,
    loginUser,
    logoutUser,
    refreshUserToken,
    checkTokenExpiry,
    hasPermission,
    isInRole,
  };
};
