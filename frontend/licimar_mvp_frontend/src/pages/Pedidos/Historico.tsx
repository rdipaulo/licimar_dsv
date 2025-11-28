import { useState, useEffect } from 'react';
import { Loader2, Download } from 'lucide-react';
import { MainLayout } from '@/components/MainLayout';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { apiService } from '@/services/api';
import { Pedido } from '@/types';

export function HistoricoPedidos() {
  const [pedidos, setPedidos] = useState<Pedido[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const { toast } = useToast();

  useEffect(() => {
    fetchPedidos();
  }, [page, statusFilter]);

  const fetchPedidos = async () => {
    setIsLoading(true);
    try {
      const response = await apiService.getPedidos({
        page,
        per_page: 10,
        status: statusFilter || undefined,
      });
      setPedidos(response.items || []);
      setTotalPages(response.pagination?.pages || 1);
      setTotalItems(response.pagination?.total || 0);
    } catch (error) {
      toast({
        title: 'Erro ao carregar pedidos',
        description: error instanceof Error ? error.message : 'Ocorreu um erro',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleImprimir = async (pedidoId: number, isFinalizado: boolean) => {
    try {
      if (isFinalizado) {
        await apiService.imprimirNotaRetorno(pedidoId);
      } else {
        await apiService.imprimirNotaSaida(pedidoId);
      }
      toast({
        title: 'Sucesso',
        description: 'Nota fiscal gerada e aberta no navegador',
      });
    } catch (error) {
      toast({
        title: 'Erro ao imprimir',
        description: error instanceof Error ? error.message : 'Ocorreu um erro',
        variant: 'destructive',
      });
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'saida':
        return 'Em Aberto';
      case 'finalizado':
        return 'Finalizado';
      case 'cancelado':
        return 'Cancelado';
      default:
        return status;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'saida':
        return 'bg-yellow-100 text-yellow-800';
      case 'finalizado':
        return 'bg-green-100 text-green-800';
      case 'cancelado':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading && pedidos.length === 0) {
    return (
      <MainLayout title="Histórico de Pedidos">
        <div className="flex justify-center items-center h-full">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout title="Histórico de Pedidos">
      <div className="space-y-6">
        {/* Filtros */}
        <Card>
          <CardHeader>
            <CardTitle>Filtros</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4 items-end">
              <div>
                <label className="block text-sm font-medium mb-2">Status</label>
                <select
                  value={statusFilter}
                  onChange={(e) => {
                    setStatusFilter(e.target.value);
                    setPage(1);
                  }}
                  className="border rounded-md px-3 py-2 text-sm"
                >
                  <option value="">Todos</option>
                  <option value="saida">Em Aberto</option>
                  <option value="finalizado">Finalizado</option>
                  <option value="cancelado">Cancelado</option>
                </select>
              </div>
              <Button onClick={() => fetchPedidos()} variant="outline">
                Filtrar
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Lista de Pedidos */}
        <Card>
          <CardHeader>
            <CardTitle>Pedidos ({totalItems})</CardTitle>
          </CardHeader>
          <CardContent>
            {pedidos.length === 0 ? (
              <p className="text-center text-gray-500 py-8">Nenhum pedido encontrado</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-4 font-semibold">ID</th>
                      <th className="text-left py-3 px-4 font-semibold">Ambulante</th>
                      <th className="text-left py-3 px-4 font-semibold">Data</th>
                      <th className="text-left py-3 px-4 font-semibold">Status</th>
                      <th className="text-right py-3 px-4 font-semibold">Total</th>
                      <th className="text-right py-3 px-4 font-semibold">Dívida</th>
                      <th className="text-center py-3 px-4 font-semibold">Ações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pedidos.map((pedido: any) => (
                      <tr key={pedido.id} className="border-b hover:bg-gray-50">
                        <td className="py-3 px-4">#{pedido.id}</td>
                        <td className="py-3 px-4">{pedido.ambulante?.nome || 'N/A'}</td>
                        <td className="py-3 px-4">
                          {new Date(pedido.data_operacao).toLocaleDateString('pt-BR')}
                        </td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(pedido.status)}`}>
                            {getStatusLabel(pedido.status)}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right font-semibold">
                          R$ {(pedido.total || 0).toFixed(2)}
                        </td>
                        <td className="py-3 px-4 text-right">
                          {pedido.divida && pedido.divida > 0 ? (
                            <span className="text-red-600 font-semibold">R$ {parseFloat(pedido.divida).toFixed(2)}</span>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-center">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleImprimir(pedido.id, pedido.status === 'finalizado')}
                            className="inline-flex items-center gap-2"
                          >
                            <Download className="h-4 w-4" />
                            Reimprimir
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Paginação */}
            {totalPages > 1 && (
              <div className="mt-6 flex justify-center gap-2">
                <Button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  variant="outline"
                >
                  Anterior
                </Button>
                {Array.from({ length: totalPages }, (_, i) => i + 1).map(p => (
                  <Button
                    key={p}
                    onClick={() => setPage(p)}
                    variant={page === p ? 'default' : 'outline'}
                  >
                    {p}
                  </Button>
                ))}
                <Button
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  variant="outline"
                >
                  Próximo
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
