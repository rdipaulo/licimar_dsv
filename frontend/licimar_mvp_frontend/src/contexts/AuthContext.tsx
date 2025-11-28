// Contexto de autenticação para gerenciar o estado do usuário

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, LoginForm } from '../types';
import { apiService } from '../services/api';
import { toast } from 'sonner';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginForm) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user;

  console.log('[AuthProvider] isLoading:', isLoading, 'user:', user);

  useEffect(() => {
    // Verifica se há token armazenado e tenta recuperar o usuário
    const initAuth = async () => {
      console.log('[AuthProvider] Iniciando autenticação...');
      try {
        const token = localStorage.getItem('access_token');
        console.log('[AuthProvider] Token encontrado:', !!token);
        
        if (token) {
          try {
            console.log('[AuthProvider] Tentando obter perfil...');
            const response = await apiService.getProfile();
            console.log('[AuthProvider] Perfil obtido:', response);
            setUser(response.user);
          } catch (error) {
            // Token inválido ou expirado
            console.warn('[AuthProvider] Erro ao recuperar perfil:', error);
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
          }
        }
      } catch (error) {
        console.error('[AuthProvider] Erro na inicialização de autenticação:', error);
      } finally {
        console.log('[AuthProvider] Autenticação concluída');
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (credentials: LoginForm) => {
    try {
      setIsLoading(true);
      const response = await apiService.login(credentials);
      
      // Armazena tokens
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      
      // Define usuário
      setUser(response.user);
      
      toast.success('Login realizado com sucesso!');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Erro ao fazer login');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await apiService.logout();
    } catch (error) {
      // Ignora erros de logout no servidor
      console.warn('Erro ao fazer logout no servidor:', error);
    } finally {
      // Remove tokens e usuário
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
      toast.success('Logout realizado com sucesso!');
    }
  };

  const refreshUser = async () => {
    try {
      const response = await apiService.getProfile();
      setUser(response.user);
    } catch (error) {
      console.error('Erro ao atualizar dados do usuário:', error);
      // Se falhar, faz logout
      logout();
    }
  };

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    logout,
    refreshUser
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
