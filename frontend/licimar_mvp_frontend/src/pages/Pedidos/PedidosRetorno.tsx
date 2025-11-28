// Caminho: src/pages/Pedidos/PedidosRetorno.tsx

import { useState, useEffect, useMemo } from 'react';
import { MainLayout } from '../../components/MainLayout';
import { apiService } from '../../services/api';
import { Pedido, ItemPedido, PedidoRetornoForm, Produto } from '../../types';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { useToast } from '../../hooks/use-toast';
import { Loader2 } from 'lucide-react';

export default function PedidosRetorno() {
  const { toast } = useToast();
  const [pedidosEmAberto, setPedidosEmAberto] = useState<Pedido[]>([]);
  const [selectedPedido, setSelectedPedido] = useState<Pedido | null>(null);
  const [retornoQuantities, setRetornoQuantities] = useState<Record<number, number>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchPedidosEmAberto();
  }, []);

  const fetchPedidosEmAberto = async () => {
    setIsLoading(true);
    try {
      const response = await apiService.getPedidos({ status: 'saida' });
      setPedidosEmAberto(response.items || []);
    } catch (error) {
      toast({
        title: 'Erro ao carregar pedidos',
        description: 'Não foi possível carregar a lista de pedidos em aberto.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectPedido = (pedido: Pedido) => {
    setSelectedPedido(pedido);
    const initialRetorno = pedido.itens.reduce((acc, item) => {
      acc[item.id] = 0;
      return acc;
    }, {} as Record<number, number>);
    setRetornoQuantities(initialRetorno);
  };

  const handleRetornoChange = (itemId: number, value: string) => {
    const quantidade = parseFloat(value);
    setRetornoQuantities(prev => ({
      ...prev,
      [itemId]: isNaN(quantidade) || quantidade < 0 ? 0 : quantidade,
    }));
  };

  const calculateItemSummary = (item: ItemPedido) => {
    const quantidadeRetorno = retornoQuantities[item.id] || 0;
    const quantidadeSaida = item.quantidade_saida;
    const quantidadeVendida = Math.max(0, quantidadeSaida - quantidadeRetorno);
    const valorTotal = quantidadeVendida * item.preco_unitario;

    return {
      quantidadeVendida,
      valorTotal,
      maxRetorno: quantidadeSaida,
    };
  };

  const totalGeral = useMemo(() => {
    if (!selectedPedido) return 0;
    return selectedPedido.itens.reduce((sum, item) => {
      const { valorTotal } = calculateItemSummary(item);
      return sum + valorTotal;
    }, 0);
  }, [selectedPedido, retornoQuantities]);

  const handleFinalizarRetorno = async () => {
    if (!selectedPedido) return;

    const payload: PedidoRetornoForm = {
      itens: selectedPedido.itens.map(item => ({
        produto_id: item.produto_id,
        quantidade_retorno: retornoQuantities[item.id] || 0,
      })),
    };

    setIsSubmitting(true);
    try {
      await apiService.registrarRetorno(selectedPedido.id, payload);
      toast({
        title: 'Sucesso',
        description: `Retorno do Pedido #${selectedPedido.id} registrado e finalizado.`,
      });
      setSelectedPedido(null);
      setRetornoQuantities({});
      fetchPedidosEmAberto();
    } catch (error) {
      toast({
        title: 'Erro ao finalizar retorno',
        description: error instanceof Error ? error.message : 'Ocorreu um erro ao tentar registrar o retorno.',
        variant: 'destructive',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <MainLayout title="Registro de Retorno/Cálculo">
        <div className="flex justify-center items-center h-full">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout title="Registro de Retorno/Cálculo">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
        {/* Coluna de Pedidos em Aberto */}
        <Card className="lg:col-span-1 overflow-y-auto">
          <CardHeader>
            <CardTitle>Pedidos em Aberto ({pedidosEmAberto.length})</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {pedidosEmAberto.length === 0 ? (
              <p className="text-center text-muted-foreground">Nenhum pedido em aberto.</p>
            ) : (
              pedidosEmAberto.map(pedido => (
                <div
                  key={pedido.id}
                  className={`p-3 border rounded-md cursor-pointer transition-colors ${selectedPedido?.id === pedido.id ? 'bg-primary/10 border-primary' : 'hover:bg-gray-50'}`}
                  onClick={() => handleSelectPedido(pedido)}
                >
                  <p className="font-semibold">Pedido #{pedido.id}</p>
                  <p className="text-sm text-muted-foreground">Ambulante: {pedido.ambulante_nome}</p>
                  <p className="text-xs text-muted-foreground">Saída: {new Date(pedido.data_operacao).toLocaleDateString()}</p>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        {/* Coluna de Detalhes e Cálculo */}
        <Card className="lg:col-span-2 flex flex-col">
          <CardHeader>
            <CardTitle>
              {selectedPedido ? `Detalhes do Pedido #${selectedPedido.id}` : 'Selecione um Pedido'}
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-grow flex flex-col">
            {!selectedPedido ? (
              <p className="text-center text-muted-foreground flex-grow flex items-center justify-center">
                Selecione um pedido na lista ao lado para registrar o retorno.
              </p>
            ) : (
              <>
                <div className="mb-4">
                  <p>
                    <strong>Ambulante:</strong> {selectedPedido.ambulante_nome}
                  </p>
                  <p>
                    <strong>Data de Saída:</strong> {new Date(selectedPedido.data_operacao).toLocaleString()}
                  </p>
                </div>

                <div className="flex-grow overflow-y-auto space-y-4 border p-4 rounded-md">
                  <h3 className="text-lg font-semibold border-b pb-2">Itens para Retorno</h3>
                  {selectedPedido.itens.map(item => {
                    const { quantidadeVendida, valorTotal, maxRetorno } = calculateItemSummary(item);
                    return (
                      <div key={item.id} className={`grid grid-cols-5 gap-4 items-center border-b pb-3 ${item.produto_nao_devolve ? 'bg-red-50/50' : ''}`}>
                        <div className="col-span-2">
                          <p className="font-medium">{item.produto_nome}</p>
                          <p className="text-sm text-muted-foreground">Saída: {item.quantidade_saida}</p>
                          <p className="text-sm text-muted-foreground">Preço Unitário: R$ {item.preco_unitario.toFixed(2)}</p>
                        </div>
                        <div className="col-span-1">
                          <label className="text-sm font-medium">Retorno</label>
                          {item.produto_nao_devolve ? (
                            <div className="mt-1 p-2 bg-gray-100 rounded text-sm text-center text-red-600">
                              Não Devolve
                            </div>
                          ) : (
                            <Input
                              type="number"
                              step={1}
                              min={0}
                              max={maxRetorno}
                              value={retornoQuantities[item.id] || 0}
                              onChange={e => handleRetornoChange(item.id, e.target.value)}
                              className="mt-1"
                            />
                          )}
                        </div>
                        <div className="col-span-1 text-center">
                          <p className="text-sm font-medium">Vendido</p>
                          <p className="font-semibold">{quantidadeVendida.toFixed(3)}</p>
                        </div>
                        <div className="col-span-1 text-right">
                          <p className="text-sm font-medium">Total</p>
                          <p className="font-bold text-primary">R$ {valorTotal.toFixed(2)}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>

                <div className="mt-4 pt-4 border-t">
                  <div className="flex justify-between text-2xl font-bold mb-4">
                    <span>Total a Pagar:</span>
                    <span>R$ {totalGeral.toFixed(2)}</span>
                  </div>
                  <Button
                    onClick={handleFinalizarRetorno}
                    className="w-full py-6 text-lg"
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                    Registrar Retorno e Finalizar Pedido
                  </Button>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
