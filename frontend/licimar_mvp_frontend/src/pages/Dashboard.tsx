// Dashboard principal com métricas e indicadores

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';
import { 
  TrendingUp, 
  DollarSign, 
  Package, 
  Users, 
  ShoppingCart,
  AlertTriangle,
  BarChart3
} from 'lucide-react';
import { apiService } from '../services/api';
import { DashboardMetrics } from '../types';
import { formatCurrency, formatDate } from '../utils';

export const Dashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadMetrics();
  }, []);

  const loadMetrics = async () => {
    try {
      setLoading(true);
      const data = await apiService.getDashboardMetrics();
      setMetrics(data);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Erro ao carregar métricas');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-8 bg-gray-200 rounded w-1/2"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Visão geral do sistema Licimar</p>
      </div>

      {/* Métricas principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Vendas Hoje</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(metrics?.vendas_hoje || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Vendas realizadas hoje
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Vendas (30 dias)</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(metrics?.vendas_periodo || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Últimos 30 dias
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Ambulantes Ativos</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {metrics?.ambulantes_ativos || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Vendedores cadastrados
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pedidos Abertos</CardTitle>
            <ShoppingCart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {metrics?.pedidos_abertos || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Aguardando retorno
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Alertas */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-yellow-500" />
              <span>Alertas</span>
            </CardTitle>
            <CardDescription>
              Produtos que requerem atenção
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {metrics?.produtos_estoque_baixo ? (
                <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <Package className="h-5 w-5 text-yellow-600" />
                    <div>
                      <p className="font-medium text-yellow-800">
                        Estoque Baixo
                      </p>
                      <p className="text-sm text-yellow-600">
                        {metrics.produtos_estoque_baixo} produto(s) com estoque baixo
                      </p>
                    </div>
                  </div>
                  <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                    {metrics.produtos_estoque_baixo}
                  </Badge>
                </div>
              ) : (
                <div className="text-center py-4 text-gray-500">
                  <Package className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p>Nenhum alerta no momento</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Produto mais vendido */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5 text-blue-500" />
              <span>Produto Mais Vendido</span>
            </CardTitle>
            <CardDescription>
              Últimos 30 dias
            </CardDescription>
          </CardHeader>
          <CardContent>
            {metrics?.produto_mais_vendido?.nome ? (
              <div className="space-y-2">
                <h3 className="font-semibold text-lg">
                  {metrics.produto_mais_vendido.nome}
                </h3>
                <p className="text-gray-600">
                  Quantidade vendida: <span className="font-medium">
                    {metrics.produto_mais_vendido.quantidade}
                  </span>
                </p>
              </div>
            ) : (
              <div className="text-center py-4 text-gray-500">
                <BarChart3 className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>Nenhuma venda registrada</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Gráfico de vendas por dia */}
      <Card>
        <CardHeader>
          <CardTitle>Vendas dos Últimos 7 Dias</CardTitle>
          <CardDescription>
            Evolução das vendas diárias
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {metrics?.vendas_por_dia?.map((venda, index) => (
              <div key={index} className="flex items-center justify-between py-2">
                <span className="text-sm text-gray-600">
                  {formatDate(venda.data)}
                </span>
                <div className="flex items-center space-x-2">
                  <div 
                    className="bg-blue-200 h-2 rounded"
                    style={{ 
                      width: `${Math.max(10, (venda.vendas / Math.max(...(metrics.vendas_por_dia?.map(v => v.vendas) || [1]))) * 100)}px` 
                    }}
                  />
                  <span className="text-sm font-medium min-w-[80px] text-right">
                    {formatCurrency(venda.vendas)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
