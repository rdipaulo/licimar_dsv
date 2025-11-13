import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Bell, Settings } from 'lucide-react';
import { Button } from './ui/button';

interface HeaderProps {
  title: string;
  sidebarOpen: boolean;
}

/**
 * Componente Header
 * Cabeçalho da página com informações do usuário e notificações
 */
const Header: React.FC<HeaderProps> = ({ title, sidebarOpen }) => {
  const { user } = useAuth();

  return (
    <header className={`bg-white border-b border-gray-200 shadow-sm transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-20'}`}>
      <div className="px-6 py-4 flex items-center justify-between">
        {/* Título da página */}
        <h1 className="text-2xl font-bold text-gray-900">{title}</h1>

        {/* Ações do header */}
        <div className="flex items-center space-x-4">
          {/* Notificações */}
          <Button
            variant="ghost"
            size="icon"
            className="relative hover:bg-gray-100"
            title="Notificações"
          >
            <Bell size={20} className="text-gray-600" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </Button>

          {/* Configurações */}
          <Button
            variant="ghost"
            size="icon"
            className="hover:bg-gray-100"
            title="Configurações"
          >
            <Settings size={20} className="text-gray-600" />
          </Button>

          {/* Separador */}
          <div className="h-6 w-px bg-gray-300"></div>

          {/* Informações do usuário */}
          <div className="flex items-center space-x-3">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">{user?.username}</p>
              <p className="text-xs text-gray-500">
                {user?.role === 'admin' ? 'Administrador' : 'Operador'}
              </p>
            </div>
            <div className="w-10 h-10 bg-indigo-600 rounded-full flex items-center justify-center text-white font-bold">
              {user?.username?.charAt(0).toUpperCase()}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
