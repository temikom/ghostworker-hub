import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authApi } from '@/lib/api';

// Minimal user info exposed to frontend - no sensitive data
interface SafeUser {
  id: string;
  name: string;
  avatarUrl?: string;
  isVerified: boolean;
  has2FA: boolean;
}

interface LoginResponse {
  success: boolean;
  requires2FA?: boolean;
  tempToken?: string;
  requiresVerification?: boolean;
}

interface AuthContextType {
  user: SafeUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  isVerified: boolean;
  login: (email: string, password: string) => Promise<LoginResponse>;
  register: (email: string, password: string, name: string) => Promise<void>;
  socialLogin: (provider: 'google' | 'microsoft' | 'facebook') => Promise<void>;
  verify2FA: (tempToken: string, code: string) => Promise<void>;
  verifyEmail: (token: string) => Promise<void>;
  resendVerification: (email: string) => Promise<void>;
  checkEmail: (email: string) => Promise<{ exists: boolean }>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Secure token storage with httpOnly-like behavior simulation
const TOKEN_KEY = 'gw_session';
const TEMP_TOKEN_KEY = 'gw_temp';

function setToken(token: string) {
  // In production, this should be an httpOnly cookie set by the server
  sessionStorage.setItem(TOKEN_KEY, token);
}

function getToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY);
}

function removeToken() {
  sessionStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(TEMP_TOKEN_KEY);
}

// Transform API user to safe user (remove sensitive fields)
function toSafeUser(user: { 
  id: string; 
  email?: string; 
  name: string; 
  avatar_url?: string;
  is_verified?: boolean;
  two_factor_enabled?: boolean;
}): SafeUser {
  return {
    id: user.id,
    name: user.name,
    avatarUrl: user.avatar_url,
    isVerified: user.is_verified ?? false,
    has2FA: user.two_factor_enabled ?? false,
    // Intentionally omit email and other sensitive data from frontend state
  };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<SafeUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = getToken();
    if (token) {
      authApi.me()
        .then((userData) => setUser(toSafeUser(userData)))
        .catch(() => removeToken())
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string): Promise<LoginResponse> => {
    const response = await authApi.login({ email, password });
    
    // Check if 2FA is required
    if (response.requires_2fa && response.temp_token) {
      return {
        success: false,
        requires2FA: true,
        tempToken: response.temp_token,
      };
    }
    
    // Check if email verification is required
    if (response.requires_verification) {
      return {
        success: false,
        requiresVerification: true,
      };
    }
    
    // Successful login
    if (response.token) {
      setToken(response.token);
      setUser(toSafeUser(response.user));
    }
    
    return { success: true };
  };

  const register = async (email: string, password: string, name: string) => {
    const response = await authApi.register({ email, password, name });
    // Don't set token immediately - require email verification
    if (response.token && response.user?.is_verified) {
      setToken(response.token);
      setUser(toSafeUser(response.user));
    }
    // User needs to verify email before accessing dashboard
  };

  const verify2FA = async (tempToken: string, code: string) => {
    const response = await authApi.verify2FA({ temp_token: tempToken, code });
    if (response.token) {
      setToken(response.token);
      setUser(toSafeUser(response.user));
    }
  };

  const verifyEmail = async (token: string) => {
    const response = await authApi.verifyEmail({ token });
    if (response.token) {
      setToken(response.token);
      setUser(toSafeUser(response.user));
    }
  };

  const resendVerification = async (email: string) => {
    await authApi.resendVerification({ email });
  };

  const checkEmail = async (email: string): Promise<{ exists: boolean }> => {
    try {
      const response = await authApi.checkEmail({ email });
      return { exists: response.exists };
    } catch {
      // For security, don't reveal if email exists
      return { exists: false };
    }
  };

  const socialLogin = async (provider: 'google' | 'microsoft' | 'facebook') => {
    // Redirect to OAuth flow - backend handles the authentication
    const redirectUrl = `${window.location.origin}/auth/callback`;
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    window.location.href = `${apiUrl}/api/v1/auth/oauth/${provider}?redirect_url=${encodeURIComponent(redirectUrl)}`;
  };

  const logout = () => {
    removeToken();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      isLoading, 
      isAuthenticated: !!user,
      isVerified: user?.isVerified ?? false,
      login, 
      register, 
      socialLogin,
      verify2FA,
      verifyEmail,
      resendVerification,
      checkEmail,
      logout 
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
