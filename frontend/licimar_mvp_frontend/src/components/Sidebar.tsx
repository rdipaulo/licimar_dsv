import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, LogOut, Users, Package, Truck, FileText, Settings, BarChart3 } from 'lucide-react';
import { Button } from './ui/button';
import { useAuth } from '../contexts/AuthContext';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  onLogout: () => void;
}

/**
 * Componente Sidebar
 * Navegação principal da aplicação com menu colapsável
 */
const Sidebar: React.FC<SidebarProps> = ({ isOpen, onToggle, onLogout }) => {
  const { user } = useAuth();
  const location = useLocation();

  const menuItems = [
    { label: 'Dashboard', icon: FileText, href: '/dashboard' },
    { label: 'Ambulantes', icon: Truck, href: '/ambulantes' },
    { label: 'Produtos', icon: Package, href: '/produtos' },
    { label: 'Pedidos', icon: BarChart3, href: '/pedidos' },
    { label: 'Usuários', icon: Users, href: '/usuarios', adminOnly: true },
    { label: 'Configurações', icon: Settings, href: '/configuracoes', adminOnly: true },
  ];

  // Filtra itens de menu baseado no role do usuário
  const visibleMenuItems = menuItems.filter(
    item => !item.adminOnly || user?.role === 'admin'
  );

  const isActive = (href: string) => location.pathname === href;

  return (
    <aside
      className={`${
        isOpen ? 'w-64' : 'w-20'
      } bg-indigo-900 text-white transition-all duration-300 flex flex-col shadow-lg fixed h-screen left-0 top-0 z-40`}
    >
      {/* Logo */}
      <div className="p-4 border-b border-indigo-800">
        <div className="flex items-center justify-between">
          <div className={`flex items-center space-x-2 ${!isOpen && 'justify-center w-full'}`}>
            <div className="w-10 h-10 bg-indigo-600 rounded-lg flex items-center justify-center font-bold text-lg">
              L
            </div>
            {isOpen && <span className="font-bold text-lg">Licimar</span>}
          </div>
          <button
            onClick={onToggle}
            className="p-1 hover:bg-indigo-800 rounded transition"
            title={isOpen ? 'Recolher' : 'Expandir'}
          >
            {isOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {/* Menu Items */}
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {visibleMenuItems.map((item) => (
          <Link
            key={item.label}
            to={item.href}
            className={`flex items-center space-x-3 p-3 rounded-lg transition ${
              isActive(item.href)
                ? 'bg-indigo-700 text-white'
                : 'hover:bg-indigo-800 text-indigo-100'
            }`}
            title={item.label}
          >
            <item.icon size={20} className="flex-shrink-0" />
            {isOpen && <span className="truncate">{item.label}</span>}
          </Link>
        ))}
      </nav>

      {/* User Info & Logout */}
      <div className="p-4 border-t border-indigo-800 space-y-3">
        {isOpen && (
          <div className="text-sm">
            <p className="font-semibold truncate">{user?.username}</p>
            <p className="text-indigo-300 text-xs truncate">{user?.email}</p>
            <p className="text-indigo-400 text-xs capitalize">
              {user?.role === 'admin' ? 'Administrador' : 'Operador'}
            </p>
          </div>
        )}
        <Button
          onClick={onLogout}
          variant="outline"
          className="w-full bg-indigo-800 hover:bg-indigo-700 border-indigo-700 text-white"
          size="sm"
        >
          <LogOut size={16} className="flex-shrink-0" />
          {isOpen && <span className="ml-2">Sair</span>}
        </Button>
      </div>
    </aside>
  );
};

export default Sidebar;
