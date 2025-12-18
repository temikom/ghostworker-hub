import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authApi } from '@/lib/api';

// Minimal user info exposed to frontend - no sensitive data
interface SafeUser {
  id: string;
  name: string;
  avatarUrl?: string;
}

interface AuthContextType {
  user: SafeUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  socialLogin: (provider: 'google' | 'microsoft' | 'facebook') => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Secure token storage with httpOnly-like behavior simulation
const TOKEN_KEY = 'gw_session';

function setToken(token: string) {
  // In production, this should be an httpOnly cookie set by the server
  sessionStorage.setItem(TOKEN_KEY, token);
}

function getToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY);
}

function removeToken() {
  sessionStorage.removeItem(TOKEN_KEY);
}

// Transform API user to safe user (remove sensitive fields)
function toSafeUser(user: { id: string; email?: string; name: string; avatar_url?: string }): SafeUser {
  return {
    id: user.id,
    name: user.name,
    avatarUrl: user.avatar_url,
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

  const login = async (email: string, password: string) => {
    const { token, user: userData } = await authApi.login({ email, password });
    setToken(token);
    setUser(toSafeUser(userData));
  };

  const register = async (email: string, password: string, name: string) => {
    const { token, user: userData } = await authApi.register({ email, password, name });
    setToken(token);
    setUser(toSafeUser(userData));
  };

  const socialLogin = async (provider: 'google' | 'microsoft' | 'facebook') => {
    // Redirect to OAuth flow - backend handles the authentication
    const redirectUrl = `${window.location.origin}/auth/callback`;
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    window.location.href = `${apiUrl}/auth/oauth/${provider}?redirect_url=${encodeURIComponent(redirectUrl)}`;
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
      login, 
      register, 
      socialLogin,
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
