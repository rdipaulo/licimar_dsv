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
  const [cobrancaDivida, setCobrancaDivida] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [saldoDevedor, setSaldoDevedor] = useState<number>(0);

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

  const handleSelectPedido = async (pedido: Pedido) => {
    setSelectedPedido(pedido);
    const initialRetorno = pedido.itens.reduce((acc, item) => {
      acc[item.id] = 0;
      return acc;
    }, {} as Record<number, number>);
    setRetornoQuantities(initialRetorno);
    setCobrancaDivida(0);

    // Carregar saldo devedor do cliente
    try {
      const dividaData = await apiService.getDividaPendente(pedido.cliente_id);
      setSaldoDevedor(dividaData.saldo_devedor || 0);
    } catch (error) {
      console.error('Erro ao carregar saldo devedor:', error);
      setSaldoDevedor(0);
    }
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
    return subtotal + cobrancaDivida;
  }, [selectedPedido, retornoQuantities, cobrancaDivida]);

  const handleFinalizarRetorno = async () => {
    if (!selectedPedido) return;

    console.log('[DEBUG] handleFinalizarRetorno iniciado com cobrancaDivida:', cobrancaDivida);

    const payload: PedidoRetornoForm = {
      itens: selectedPedido.itens.map(item => ({
        produto_id: item.produto_id,
        quantidade_retorno: retornoQuantities[item.id] || 0,
      })),
    };

    setIsSubmitting(true);
    try {
      // Payload com cobrança de dívida
      const payloadComDivida = {
        ...payload,
        divida: cobrancaDivida,
      };
      
      // DEBUG: Log do payload
      console.log('[DEBUG] Payload enviado para registrarRetorno:', JSON.stringify(payloadComDivida, null, 2));
      console.log('[DEBUG] Valor de cobrancaDivida:', cobrancaDivida, typeof cobrancaDivida);

      await apiService.registrarRetorno(selectedPedido.id, payloadComDivida);
      
      // Registrar pagamento de dívida se o campo foi preenchido
      if (cobrancaDivida > 0) {
        try {
          console.log(`[DEBUG] Registrando pagamento de dívida: Cliente ${selectedPedido.cliente_id}, Valor R$ ${cobrancaDivida}`);
          await apiService.registrarPagamentoDivida({
            id_cliente: selectedPedido.cliente_id,
            cobranca_divida: cobrancaDivida,
            descricao: `Cobrança do Pedido de Retorno #${selectedPedido.id}`,
          });
          console.log('[DEBUG] Pagamento de dívida registrado com sucesso');
        } catch (error) {
          console.error('[ERROR] Erro ao registrar pagamento de dívida:', error);
          toast({
            title: 'Aviso',
            description: 'Retorno registrado, mas houve erro ao registrar o pagamento de dívida.',
            variant: 'destructive',
          });
        }
      }
      
      // IMPRIMIR NOTA FISCAL FINAL (Requisito do Usuário)
      try {
        console.log(`[DEBUG] Iniciando impressão da nota de retorno para pedido ${selectedPedido.id}`);
        const blob = await apiService.imprimirNotaRetorno(selectedPedido.id);
        
        // Trigger download do PDF
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `nota_fiscal_retorno_pedido_${selectedPedido.id}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
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
      setCobrancaDivida(0);
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
                {/* Client information section */}
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
                  {selectedPedido.itens
                    .filter(item => !item.produto_nao_devolve)
                    .map(item => {
                    const { quantidadeVendida, valorTotal, maxRetorno } = calculateItemSummary(item);
                    return (
                      <div key={item.id} className={`grid grid-cols-6 gap-2 items-center border-b pb-3 text-sm`}>
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
                    <span>R$ {(totalGeral - cobrancaDivida).toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between items-center mb-4">
                    <Label htmlFor="cobrancaDivida" className="text-lg font-semibold">Cobrança de Dívida:</Label>
                    <div className="space-y-2">
                      <input
                        id="cobrancaDivida"
                        type="number"
                        inputMode="decimal"
                        step="0.01"
                        min="0"
                        value={cobrancaDivida}
                        onChange={(e) => {
                          const valor = parseFloat(e.target.value) || 0;
                          console.log('[DEBUG] cobrancaDivida onChange:', valor);
                          setCobrancaDivida(Math.max(0, valor));
                        }}
                        placeholder="0.00"
                        className="border rounded px-2 py-1 text-right w-32"
                      />
                      {saldoDevedor > 0 && (
                        <p className="text-sm text-orange-600 font-medium">
                          Saldo devedor: R$ {saldoDevedor.toFixed(2)}
                        </p>
                      )}
                    </div>
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
