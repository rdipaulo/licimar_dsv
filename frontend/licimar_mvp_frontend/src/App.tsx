import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'sonner';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginPage from './pages/Login';
import DashboardPage from './pages/Dashboard';
import ClientesPage from './pages/Clientes';
import ProdutosPage from './pages/Produtos';
import PedidosSaida from './pages/Pedidos/PedidosSaida';
import PedidosRetorno from './pages/Pedidos/PedidosRetorno';
import { HistoricoPedidos } from './pages/Pedidos/Historico';
import { DashboardDivida } from './pages/DashboardDivida';
import LoadingSpinner from './components/LoadingSpinner';

/**
 * Componente de conteúdo da aplicação protegido por autenticação
 */
const AppContent: React.FC = () => {
  const { isLoading, isAuthenticated } = useAuth();

  console.log('[AppContent] Rendering - isLoading:', isLoading, 'isAuthenticated:', isAuthenticated);

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <Routes>
      {/* Rota de login */}
      <Route 
        path="/login" 
        element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />} 
      />

      {/* Rotas protegidas - redirecionam para login se não autenticado */}
      <Route 
        path="/dashboard" 
        element={isAuthenticated ? <DashboardPage /> : <Navigate to="/login" replace />} 
      />

      <Route 
        path="/clientes" 
        element={isAuthenticated ? <ClientesPage /> : <Navigate to="/login" replace />} 
      />

      <Route 
        path="/produtos" 
        element={isAuthenticated ? <ProdutosPage /> : <Navigate to="/login" replace />} 
      />

      <Route 
        path="/pedidos/saida" 
        element={isAuthenticated ? <PedidosSaida /> : <Navigate to="/login" replace />} 
      />

      <Route 
        path="/pedidos/retorno" 
        element={isAuthenticated ? <PedidosRetorno /> : <Navigate to="/login" replace />} 
      />

      <Route 
        path="/pedidos/historico" 
        element={isAuthenticated ? <HistoricoPedidos /> : <Navigate to="/login" replace />} 
      />

      <Route 
        path="/dashboard-divida" 
        element={isAuthenticated ? <DashboardDivida /> : <Navigate to="/login" replace />} 
      />

      {/* Rota padrão */}
      <Route path="/" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />} />

      {/* Rota 404 */}
      <Route path="*" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />} />
    </Routes>
  );
};

/**
 * Componente raiz da aplicação
 */
const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
      <Toaster position="top-right" />
    </AuthProvider>
  );
};

export default App;
