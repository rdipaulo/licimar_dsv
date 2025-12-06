import { useState, useEffect } from 'react';
import { Loader2, Download, Plus, X } from 'lucide-react';
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
  const [showDividaModal, setShowDividaModal] = useState(false);
  const [selectedClienteId, setSelectedClienteId] = useState<number | null>(null);
  const [selectedClienteNome, setSelectedClienteNome] = useState<string>('');
  const [novaDivida, setNovaDivida] = useState<string>('0');
  const [dividaDescription, setDividaDescription] = useState<string>('');
  const [isSubmittingDivida, setIsSubmittingDivida] = useState(false);
  const [clientesSaldos, setClientesSaldos] = useState<Record<number, number>>({});
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

      // Carrega saldos dos clientes
      if (response.items && response.items.length > 0) {
        const clienteIds = new Set(response.items.map((p: any) => p.cliente_id).filter(Boolean));
        for (const clienteId of Array.from(clienteIds)) {
          try {
            const saldoResponse = await apiService.getDividaPendente(clienteId as number);
            setClientesSaldos(prev => ({
              ...prev,
              [clienteId]: saldoResponse.saldo_devedor || 0
            }));
          } catch (error) {
            console.error(`Erro ao carregar saldo do cliente ${clienteId}:`, error);
          }
        }
      }
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

  const handleAbrirModalDivida = (clienteId: number, clienteNome: string) => {
    setSelectedClienteId(clienteId);
    setSelectedClienteNome(clienteNome);
    setNovaDivida('0');
    setDividaDescription('');
    setShowDividaModal(true);
  };

  const handleRegistrarDivida = async () => {
    if (!selectedClienteId) return;

    const valor = parseFloat(novaDivida);
    if (isNaN(valor) || valor <= 0) {
      toast({
        title: 'Erro de validação',
        description: 'O valor da dívida deve ser maior que 0',
        variant: 'destructive',
      });
      return;
    }

    setIsSubmittingDivida(true);
    try {
      await apiService.registrarDivida({
        id_cliente: selectedClienteId,
        valor_divida: valor,
        descricao: dividaDescription || `Débito de ${selectedClienteNome}`,
      });

      toast({
        title: 'Sucesso',
        description: `Dívida de R$ ${valor.toFixed(2)} registrada para ${selectedClienteNome}`,
      });

      // Recarrega os dados
      setShowDividaModal(false);
      await fetchPedidos();
    } catch (error) {
      toast({
        title: 'Erro ao registrar dívida',
        description: error instanceof Error ? error.message : 'Ocorreu um erro',
        variant: 'destructive',
      });
    } finally {
      setIsSubmittingDivida(false);
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
                  title="Filtrar pedidos por status"
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
                      <th className="text-left py-3 px-4 font-semibold">cliente</th>
                      <th className="text-left py-3 px-4 font-semibold">Data</th>
                      <th className="text-left py-3 px-4 font-semibold">Status</th>
                      <th className="text-right py-3 px-4 font-semibold">Total</th>
                      <th className="text-right py-3 px-4 font-semibold">Dívida</th>
                      <th className="text-right py-3 px-4 font-semibold">Saldo Devedor</th>
                      <th className="text-center py-3 px-4 font-semibold">Ações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pedidos.map((pedido: any) => (
                      <tr key={pedido.id} className="border-b hover:bg-gray-50">
                        <td className="py-3 px-4">#{pedido.id}</td>
                        <td className="py-3 px-4">{pedido.cliente_nome || pedido.ambulante_nome || 'N/A'}</td>
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
                        <td className="py-3 px-4 text-right">
                          {clientesSaldos[pedido.cliente_id] && clientesSaldos[pedido.cliente_id] > 0 ? (
                            <span className="text-orange-600 font-semibold">R$ {clientesSaldos[pedido.cliente_id].toFixed(2)}</span>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-center space-x-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleAbrirModalDivida(pedido.cliente_id, pedido.cliente_nome)}
                            className="inline-flex items-center gap-1"
                            title="Lançar novo débito para este cliente"
                          >
                            <Plus className="h-4 w-4" />
                            Débito
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleImprimir(pedido.id, pedido.status === 'finalizado')}
                            className="inline-flex items-center gap-1"
                          >
                            <Download className="h-4 w-4" />
                            PDF
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

        {/* Modal de Lançamento de Dívida */}
        {showDividaModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <Card className="w-full max-w-md">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
                <CardTitle>Lançar Débito</CardTitle>
                <button
                  onClick={() => setShowDividaModal(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <X className="h-5 w-5" />
                </button>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm font-medium text-gray-600">Cliente</p>
                  <p className="text-lg font-semibold">{selectedClienteNome}</p>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Valor da Dívida (R$) *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={novaDivida}
                    onChange={(e) => setNovaDivida(e.target.value)}
                    placeholder="0.00"
                    className="w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={isSubmittingDivida}
                  />
                  <p className="text-xs text-gray-500 mt-1">Deve ser maior que 0</p>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Descrição (opcional)
                  </label>
                  <textarea
                    value={dividaDescription}
                    onChange={(e) => setDividaDescription(e.target.value)}
                    placeholder="Ex: Débito acumulado, pagamento pendente..."
                    className="w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    disabled={isSubmittingDivida}
                  />
                </div>

                {clientesSaldos[selectedClienteId] && clientesSaldos[selectedClienteId] > 0 && (
                  <div className="bg-orange-50 border border-orange-200 rounded-md p-3">
                    <p className="text-sm">
                      <strong>Saldo devedor atual:</strong>{' '}
                      <span className="text-orange-600 font-semibold">
                        R$ {clientesSaldos[selectedClienteId].toFixed(2)}
                      </span>
                    </p>
                  </div>
                )}

                <div className="flex gap-3 pt-4">
                  <Button
                    onClick={() => setShowDividaModal(false)}
                    variant="outline"
                    className="flex-1"
                    disabled={isSubmittingDivida}
                  >
                    Cancelar
                  </Button>
                  <Button
                    onClick={handleRegistrarDivida}
                    className="flex-1 bg-blue-600 hover:bg-blue-700"
                    disabled={isSubmittingDivida}
                  >
                    {isSubmittingDivida ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Registrando...
                      </>
                    ) : (
                      'Registrar Débito'
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
