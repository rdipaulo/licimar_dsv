// Layout principal da aplicação com navegação

import React, { useState } from 'react';
import { Link, useLocation, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from './ui/button';
import { Avatar, AvatarFallback } from './ui/avatar';
import { Badge } from './ui/badge';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuLabel, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from './ui/dropdown-menu';
import { Sheet, SheetContent, SheetTrigger } from './ui/sheet';
import { 
  Home, 
  Package, 
  ShoppingCart, 
  Settings, 
  Menu, 
  LogOut, 
  User,
  BarChart3,
  Users,
  Tags,
  Calculator,
  FileText,
  Activity
} from 'lucide-react';
import { getInitials, getColorFromString } from '../utils';

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Saída de Produtos', href: '/saida', icon: Package },
  { name: 'Retorno e Cálculo', href: '/retorno', icon: ShoppingCart },
];

const adminNavigation = [
  { name: 'clientes', href: '/gerenciar/clientes', icon: Users },
  { name: 'Produtos', href: '/gerenciar/produtos', icon: Package },
  { name: 'Categorias', href: '/gerenciar/categorias', icon: Tags },
  { name: 'Regras de Cobrança', href: '/gerenciar/regras', icon: Calculator },
  { name: 'Usuários', href: '/gerenciar/usuarios', icon: User },
  { name: 'Relatórios', href: '/gerenciar/relatorios', icon: BarChart3 },
  { name: 'Logs', href: '/gerenciar/logs', icon: Activity },
];

export const Layout: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const isActive = (href: string) => {
    if (href === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(href);
  };

  const handleLogout = () => {
    logout();
  };

  const NavLink = ({ item, mobile = false }: { item: any; mobile?: boolean }) => (
    <Link
      to={item.href}
      className={`
        flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors
        ${isActive(item.href)
          ? 'bg-blue-100 text-blue-700'
          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
        }
        ${mobile ? 'w-full' : ''}
      `}
      onClick={() => mobile && setSidebarOpen(false)}
    >
      <item.icon className="mr-3 h-5 w-5" />
      {item.name}
    </Link>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo e navegação mobile */}
            <div className="flex items-center">
              <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
                <SheetTrigger asChild>
                  <Button variant="ghost" size="sm" className="lg:hidden">
                    <Menu className="h-5 w-5" />
                  </Button>
                </SheetTrigger>
                <SheetContent side="left" className="w-80">
                  <div className="py-4">
                    <h2 className="text-lg font-semibold mb-4">Sistema Licimar</h2>
                    <nav className="space-y-2">
                      {navigation.map((item) => (
                        <NavLink key={item.name} item={item} mobile />
                      ))}
                      
                      {user?.role === 'admin' && (
                        <>
                          <div className="pt-4 pb-2">
                            <h3 className="text-sm font-medium text-gray-500 px-3">
                              Gerenciar
                            </h3>
                          </div>
                          {adminNavigation.map((item) => (
                            <NavLink key={item.name} item={item} mobile />
                          ))}
                        </>
                      )}
                    </nav>
                  </div>
                </SheetContent>
              </Sheet>

              <Link to="/" className="flex items-center space-x-2 ml-2">
                <div className="bg-blue-600 text-white p-2 rounded-lg">
                  <Package className="h-6 w-6" />
                </div>
                <span className="text-xl font-bold text-gray-900 hidden sm:block">
                  Licimar
                </span>
              </Link>
            </div>

            {/* Navegação desktop */}
            <nav className="hidden lg:flex space-x-1">
              {navigation.map((item) => (
                <NavLink key={item.name} item={item} />
              ))}
            </nav>

            {/* Menu do usuário */}
            <div className="flex items-center space-x-4">
              {user?.role === 'admin' && (
                <Badge variant="secondary" className="hidden sm:inline-flex">
                  Administrador
                </Badge>
              )}
              
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                    <Avatar className="h-8 w-8">
                      <AvatarFallback className={getColorFromString(user?.username || '')}>
                        {getInitials(user?.username || 'U')}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end" forceMount>
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium leading-none">
                        {user?.username}
                      </p>
                      <p className="text-xs leading-none text-muted-foreground">
                        {user?.email}
                      </p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link to="/perfil" className="flex items-center">
                      <User className="mr-2 h-4 w-4" />
                      Perfil
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to="/configuracoes" className="flex items-center">
                      <Settings className="mr-2 h-4 w-4" />
                      Configurações
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout}>
                    <LogOut className="mr-2 h-4 w-4" />
                    Sair
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar desktop */}
        <aside className="hidden lg:flex lg:flex-col lg:w-64 lg:fixed lg:inset-y-0 lg:pt-16 lg:bg-white lg:border-r">
          <div className="flex-1 flex flex-col overflow-y-auto">
            <nav className="flex-1 px-4 py-6 space-y-2">
              {user?.role === 'admin' && (
                <>
                  <div className="pb-2">
                    <h3 className="text-sm font-medium text-gray-500 px-3">
                      Gerenciar
                    </h3>
                  </div>
                  {adminNavigation.map((item) => (
                    <NavLink key={item.name} item={item} />
                  ))}
                </>
              )}
            </nav>
          </div>
        </aside>

        {/* Conteúdo principal */}
        <main className="flex-1 lg:pl-64">
          <div className="py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <Outlet />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};
