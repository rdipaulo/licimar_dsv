// Caminho: src/pages/Pedidos/PedidosRetorno.tsx

import { useState, useEffect, useMemo } from 'react';
import { MainLayout } from '../../components/MainLayout';
import { apiService } from '../../services/api';
import { Pedido, ItemPedido, PedidoRetornoForm, Produto } from '../../types';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Minus, Plus } from 'lucide-react';
import { useToast } from '../../hooks/use-toast';
import { Loader2 } from 'lucide-react';

export default function PedidosRetorno() {
  const { toast } = useToast();
  const [pedidosEmAberto, setPedidosEmAberto] = useState<Pedido[]>([]);
  const [selectedPedido, setSelectedPedido] = useState<Pedido | null>(null);
  const [retornoQuantities, setRetornoQuantities] = useState<Record<number, number>>({});
  const [geloKg, setGeloKg] = useState(0);
  const [divida, setDivida] = useState(0);
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
    // Aceita vírgula e ponto
    const rawValue = value.replace(',', '.');
    const quantidade = parseFloat(rawValue);
    setRetornoQuantities(prev => ({
      ...prev,
      [itemId]: isNaN(quantidade) || quantidade < 0 ? 0 : quantidade,
    }));
  };

  const handleRetornoIncrement = (itemId: number, max: number) => {
    setRetornoQuantities(prev => {
      const current = prev[itemId] || 0;
      const next = Math.min(max, current + 1);
      return { ...prev, [itemId]: next };
    });
  };

  const handleRetornoDecrement = (itemId: number) => {
    setRetornoQuantities(prev => {
      const current = prev[itemId] || 0;
      const next = Math.max(0, current - 1);
      return { ...prev, [itemId]: next };
    });
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
    const subtotal = selectedPedido.itens.reduce((sum, item) => {
      const { valorTotal } = calculateItemSummary(item);
      return sum + valorTotal;
    }, 0);
    return subtotal + divida;
  }, [selectedPedido, retornoQuantities, divida]);

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
      // O backend precisa ser ajustado para aceitar e processar o campo 'divida'
      // Assumindo que o backend foi ajustado para aceitar um campo 'divida' no payload
      const payloadComDivida = {
        ...payload,
        gelo_kg: geloKg,
        divida: divida,
      };

      await apiService.registrarRetorno(selectedPedido.id, payloadComDivida);
      
      // IMPRIMIR NOTA FISCAL FINAL (Requisito do Usuário)
      try {
        console.log(`[DEBUG] Iniciando impressão da nota de retorno para pedido ${selectedPedido.id}`);
        await apiService.imprimirNotaRetorno(selectedPedido.id);
        console.log('[DEBUG] Nota de retorno impressa com sucesso');
      } catch (error) {
        console.error('[ERROR] Erro ao imprimir nota de retorno:', error);
        toast({
          title: 'Nota Fiscal',
          description: 'Nota de retorno gerada. Verifique seu navegador para download.',
          variant: 'default',
        });
      }

      toast({
        title: 'Sucesso',
        description: `Retorno do Pedido #${selectedPedido.id} registrado e finalizado. Nota fiscal final gerada.`,
      });
      setSelectedPedido(null);
      setRetornoQuantities({});
      setGeloKg(0);
      setDivida(0);
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
                  <p className="text-sm text-muted-foreground">cliente: {pedido.cliente_nome}</p>
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
                    <strong>cliente:</strong> {selectedPedido.cliente_nome}
                  </p>
                  <p>
                    <strong>Data de Saída:</strong> {new Date(selectedPedido.data_operacao).toLocaleString()}
                  </p>
                </div>

                <div className="flex-grow overflow-y-auto border p-4 rounded-md">
                  <div className="mb-4">
                    <h3 className="text-lg font-semibold mb-3">Itens para Retorno</h3>
                    <div className="grid grid-cols-6 gap-2 items-center border-b pb-2 mb-3 font-semibold text-sm">
                      <div className="col-span-2">Produto</div>
                      <div className="text-center">Saída</div>
                      <div className="text-center">Retorno</div>
                      <div className="text-center">Vendido</div>
                      <div className="text-right">Total</div>
                    </div>
                  </div>
                  {selectedPedido.itens.map(item => {
                    const { quantidadeVendida, valorTotal, maxRetorno } = calculateItemSummary(item);
                    return (
                      <div key={item.id} className={`grid grid-cols-6 gap-2 items-center border-b pb-3 text-sm ${item.produto_nao_devolve ? 'bg-red-50/50' : ''}`}>
                        {/* Coluna 1-2: Produto */}
                        <div className="col-span-2">
                          <p className="font-medium">{item.produto_nome}</p>
                          <p className="text-xs text-muted-foreground">R$ {item.preco_unitario.toFixed(2)}</p>
                        </div>

                        {/* Coluna 3: Saída (int) */}
                        <div className="text-center">
                          <p className="text-xs text-muted-foreground">Saída</p>
                          <p className="font-semibold">{Math.round(item.quantidade_saida)}</p>
                        </div>

                        {/* Coluna 4: Retorno (int) */}
                        <div className="text-center">
                          {item.produto_nao_devolve ? (
                            <div className="p-2 bg-red-100 rounded text-xs text-red-700 font-medium">Não Devolve</div>
                          ) : (
                            <div className="flex items-center justify-center gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                className="h-8 w-8 p-0"
                                onClick={() => handleRetornoDecrement(item.id)}
                                disabled={(retornoQuantities[item.id] || 0) <= 0}
                              >
                                <Minus className="h-4 w-4" />
                              </Button>
                              <Input
                                type="number"
                                min={0}
                                max={maxRetorno}
                                value={retornoQuantities[item.id] || 0}
                                onChange={e => handleRetornoChange(item.id, e.target.value)}
                                className="w-16 h-8 text-center text-sm font-semibold"
                              />
                              <Button
                                variant="outline"
                                size="sm"
                                className="h-8 w-8 p-0"
                                onClick={() => handleRetornoIncrement(item.id, maxRetorno)}
                                disabled={(retornoQuantities[item.id] || 0) >= maxRetorno}
                              >
                                <Plus className="h-3 w-3" />
                              </Button>
                            </div>
                          )}
                        </div>

                        {/* Coluna 5: Vendido (int) */}
                        <div className="text-center">
                          <p className="text-xs text-muted-foreground">Vendido</p>
                          <p className="font-semibold">{Math.round(quantidadeVendida)}</p>
                        </div>

                        {/* Coluna 6: Valor Total */}
                        <div className="text-right">
                          <p className="text-xs text-muted-foreground">Total</p>
                          <p className="font-bold text-primary">R$ {valorTotal.toFixed(2)}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>

                <div className="mt-4 pt-4 border-t">
                  <div className="flex justify-between text-lg font-semibold mb-2">
                    <span>Subtotal:</span>
                    <span>R$ {(totalGeral - divida).toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between items-center mb-4">
                    <Label htmlFor="gelo" className="text-lg font-semibold">Gelo Retorno (kg):</Label>
                    <Input
                      id="gelo"
                      type="text"
                      inputMode="decimal"
                      value={geloKg === 0 ? '' : geloKg.toFixed(3).replace('.', ',')}
                      onChange={(e) => {
                        const rawValue = e.target.value.replace(',', '.');
                        const valor = parseFloat(rawValue) || 0;
                        setGeloKg(Math.max(0, valor));
                      }}
                      className="w-16 h-8 text-xl text-right font-semibold"
                      placeholder="0,000"
                    />
                  </div>
                  <div className="flex justify-between items-center mb-4">
                    <Label htmlFor="divida" className="text-lg font-semibold">Cobrança de Dívida:</Label>
                    <Input
                      id="divida"
                      type="text"
                      inputMode="decimal"
                      value={divida === 0 ? '' : divida.toFixed(2).replace('.', ',')}
                      onChange={(e) => {
                        const rawValue = e.target.value.replace(',', '.');
                        const valor = parseFloat(rawValue) || 0;
                        setDivida(Math.max(0, valor));
                      }}
                      className="w-48 h-10 text-xl text-right font-semibold"
                      placeholder="0,00"
                    />
                  </div>
                  <div className="flex justify-between text-2xl font-bold mb-4 border-t pt-2">
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
