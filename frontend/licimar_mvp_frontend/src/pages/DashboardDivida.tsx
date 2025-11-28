import { useState, useEffect } from 'react';
import { Loader2, TrendingUp, DollarSign } from 'lucide-react';
import { MainLayout } from '@/components/MainLayout';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { apiService } from '@/services/api';
import { Ambulante } from '@/types';

interface DebtSummary {
  ambulante: Ambulante;
  totalDivida: number;
  totalPedidos: number;
  ultimoPedido?: string;
}

export function DashboardDivida() {
  const [debtSummaries, setDebtSummaries] = useState<DebtSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [totalDivida, setTotalDivida] = useState(0);
  const { toast } = useToast();

  useEffect(() => {
    fetchDebtData();
  }, []);

  const fetchDebtData = async () => {
    setIsLoading(true);
    try {
      // Fetch all ambulantes
      const ambulantesResponse = await apiService.getAmbulantes({
        per_page: 100,
      });
      const ambulantesList = ambulantesResponse.items || [];

      // Fetch all finished pedidos
      const pedidosResponse = await apiService.getPedidos({
        status: 'finalizado',
        per_page: 1000,
      });
      const pedidos = pedidosResponse.items || [];

      // Calculate debt by ambulante
      const debtMap = new Map<number, { ambulante: Ambulante; divida: number; pedidoCount: number; ultimoPedido?: string }>();

      ambulantesList.forEach((ambulante: Ambulante) => {
        if (!debtMap.has(ambulante.id)) {
          debtMap.set(ambulante.id, {
            ambulante,
            divida: 0,
            pedidoCount: 0,
          });
        }
      });

      pedidos.forEach((pedido: any) => {
        const entry = debtMap.get(pedido.ambulante_id);
        if (entry) {
          entry.divida += parseFloat(pedido.divida || 0);
          entry.pedidoCount += 1;
          entry.ultimoPedido = new Date(pedido.data_operacao).toLocaleDateString('pt-BR');
        }
      });

      // Convert map to array and sort by debt amount
      const summaries: DebtSummary[] = Array.from(debtMap.values())
        .filter(entry => entry.divida > 0) // Only show ambulantes with debt
        .map(entry => ({
          ambulante: entry.ambulante,
          totalDivida: entry.divida,
          totalPedidos: entry.pedidoCount,
          ultimoPedido: entry.ultimoPedido,
        }))
        .sort((a, b) => b.totalDivida - a.totalDivida);

      setDebtSummaries(summaries);

      // Calculate total debt
      const total = summaries.reduce((sum, item) => sum + item.totalDivida, 0);
      setTotalDivida(total);
    } catch (error) {
      toast({
        title: 'Erro ao carregar dados de dívida',
        description: error instanceof Error ? error.message : 'Ocorreu um erro',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <MainLayout title="Dashboard de Dívida">
        <div className="flex justify-center items-center h-full">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout title="Dashboard de Dívida">
      <div className="space-y-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 mb-1">Dívida Total</p>
                  <p className="text-3xl font-bold text-red-600">
                    R$ {totalDivida.toFixed(2)}
                  </p>
                </div>
                <DollarSign className="h-12 w-12 text-red-200" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 mb-1">Ambulantes com Dívida</p>
                  <p className="text-3xl font-bold text-orange-600">
                    {debtSummaries.length}
                  </p>
                </div>
                <TrendingUp className="h-12 w-12 text-orange-200" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 mb-1">Dívida Média</p>
                  <p className="text-3xl font-bold text-blue-600">
                    R$ {debtSummaries.length > 0 ? (totalDivida / debtSummaries.length).toFixed(2) : '0.00'}
                  </p>
                </div>
                <DollarSign className="h-12 w-12 text-blue-200" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Debt List */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Detalhamento de Dívidas</CardTitle>
              <Button onClick={fetchDebtData} variant="outline" size="sm">
                Atualizar
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {debtSummaries.length === 0 ? (
              <p className="text-center text-gray-500 py-8">Nenhuma dívida registrada!</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-4 font-semibold">Ambulante</th>
                      <th className="text-left py-3 px-4 font-semibold">CPF</th>
                      <th className="text-left py-3 px-4 font-semibold">Telefone</th>
                      <th className="text-right py-3 px-4 font-semibold">Dívida Total</th>
                      <th className="text-center py-3 px-4 font-semibold">Pedidos</th>
                      <th className="text-center py-3 px-4 font-semibold">Último Pedido</th>
                      <th className="text-center py-3 px-4 font-semibold">% do Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {debtSummaries.map((item) => (
                      <tr key={item.ambulante.id} className="border-b hover:bg-gray-50">
                        <td className="py-3 px-4">
                          <div>
                            <p className="font-semibold">{item.ambulante.nome}</p>
                          </div>
                        </td>
                        <td className="py-3 px-4">{item.ambulante.cpf || '-'}</td>
                        <td className="py-3 px-4">{item.ambulante.telefone || '-'}</td>
                        <td className="py-3 px-4 text-right">
                          <span className="font-bold text-red-600">R$ {item.totalDivida.toFixed(2)}</span>
                        </td>
                        <td className="py-3 px-4 text-center">
                          <span className="bg-gray-200 text-gray-800 px-2 py-1 rounded-full text-xs font-semibold">
                            {item.totalPedidos}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-center">
                          {item.ultimoPedido ? (
                            <span className="text-sm">{item.ultimoPedido}</span>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-center">
                          <span className="text-sm font-semibold">
                            {((item.totalDivida / totalDivida) * 100).toFixed(1)}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
