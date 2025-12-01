import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Users, Package, ShoppingCart, TrendingUp } from 'lucide-react';
import MainLayout from '../components/MainLayout';

/**
 * Página Dashboard
 * Visão geral do sistema com métricas e indicadores
 */
const DashboardPage: React.FC = () => {
  // Dados de exemplo (em produção, viriam da API)
  const metrics = {
    clientesAtivos: 5,
    produtosEmEstoque: 10,
    pedidosAbertos: 0,
    usuariosAtivos: 2,
  };

  return (
    <MainLayout title="Dashboard">
      <div className="space-y-6">
        {/* Cards de Métricas */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Card 1: clientes */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">clientes Ativos</CardTitle>
              <Users className="h-4 w-4 text-indigo-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.clientesAtivos}</div>
              <p className="text-xs text-gray-500 mt-1">Cadastrados no sistema</p>
            </CardContent>
          </Card>

          {/* Card 2: Produtos */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Produtos em Estoque</CardTitle>
              <Package className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.produtosEmEstoque}</div>
              <p className="text-xs text-gray-500 mt-1">Disponíveis</p>
            </CardContent>
          </Card>

          {/* Card 3: Pedidos */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pedidos Abertos</CardTitle>
              <ShoppingCart className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.pedidosAbertos}</div>
              <p className="text-xs text-gray-500 mt-1">Aguardando processamento</p>
            </CardContent>
          </Card>

          {/* Card 4: Usuários */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Usuários Ativos</CardTitle>
              <TrendingUp className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.usuariosAtivos}</div>
              <p className="text-xs text-gray-500 mt-1">No sistema</p>
            </CardContent>
          </Card>
        </div>

        {/* Bem-vindo */}
        <Card>
          <CardHeader>
            <CardTitle>Bem-vindo ao Licimar MVP</CardTitle>
            <CardDescription>
              Sistema de Gestão de clientes e Produtos
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-gray-700">
                Bem-vindo ao Licimar MVP! Este é um sistema de gestão completo para controlar clientes, produtos, estoque e pedidos.
              </p>
              <p className="text-gray-600 text-sm">
                Use o menu lateral para navegar entre as diferentes seções do sistema. Você pode gerenciar clientes, produtos, pedidos e muito mais.
              </p>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-900">
                  <strong>💡 Dica:</strong> Clique no ícone de menu para expandir ou recolher a barra lateral.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Seção de Atividades Recentes (Placeholder) */}
        <Card>
          <CardHeader>
            <CardTitle>Atividades Recentes</CardTitle>
            <CardDescription>
              Últimas operações realizadas no sistema
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 border-b">
                <div>
                  <p className="font-medium text-sm">Login realizado</p>
                  <p className="text-xs text-gray-500">Há 2 minutos</p>
                </div>
                <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Sucesso</span>
              </div>
              <div className="flex items-center justify-between p-3 border-b">
                <div>
                  <p className="font-medium text-sm">Pedido criado</p>
                  <p className="text-xs text-gray-500">Há 1 hora</p>
                </div>
                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">Novo</span>
              </div>
              <div className="flex items-center justify-between p-3">
                <div>
                  <p className="font-medium text-sm">Estoque atualizado</p>
                  <p className="text-xs text-gray-500">Há 3 horas</p>
                </div>
                <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">Atualização</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
};

export default DashboardPage;
