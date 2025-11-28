// Caminho: src/pages/Pedidos/PedidosSaida.tsx

import { useState, useEffect, useMemo } from 'react';
import { MainLayout } from '../../components/MainLayout';
import { apiService } from '../../services/api';
import { Ambulante, Produto, PedidoSaidaForm, Pedido } from '../../types';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { useToast } from '../../hooks/use-toast';
import { Loader2 } from 'lucide-react';

interface CarrinhoItem {
  produto_id: number;
  produto_nome: string;
  preco_unitario: number;
  quantidade_saida: number;
  valor_total: number;
}

export default function PedidosSaida() {
  const { toast } = useToast();
  const [ambulantes, setAmbulantes] = useState<Ambulante[]>([]);
  const [produtos, setProdutos] = useState<Produto[]>([]);
  const [selectedAmbulanteId, setSelectedAmbulanteId] = useState<number | null>(null);
  const [pedidoEmEdicao, setPedidoEmEdicao] = useState<Pedido | null>(null);
  const [carrinho, setCarrinho] = useState<CarrinhoItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    async function fetchData() {
      try {
        const ambulantesRes = await apiService.getAmbulantesAtivos();
        const produtosRes = await apiService.getProdutos();
        // Não carrega pedidos em aberto na inicialização, a lógica será movida para o useEffect do selectedAmbulanteId
        // const pedidosEmAbertoRes = await apiService.getPedidos({ status: 'saida' });

        setAmbulantes(ambulantesRes);
        setProdutos(produtosRes.items || []);
        
        // Lógica de carregamento de pedido em aberto movida para o useEffect do selectedAmbulanteId
      } catch (error) {
        toast({
          title: 'Erro ao carregar dados',
          description: 'Não foi possível carregar a lista de ambulantes e produtos.',
          variant: 'destructive',
        });
      } finally {
        setIsLoading(false);
      }
    }
    fetchData();
  }, []);

  // Efeito para carregar pedido em aberto quando o ambulante é selecionado
  useEffect(() => {
    if (!selectedAmbulanteId) {
      setPedidoEmEdicao(null);
      setCarrinho([]);
      return;
    }

    async function fetchPedidoEmAberto() {
      try {
        // Busca pedidos em aberto para o ambulante selecionado
        const pedidosRes = await apiService.getPedidos({ status: 'saida', ambulante_id: selectedAmbulanteId });
        
        if (pedidosRes.items && pedidosRes.items.length > 0) {
          const pedido = pedidosRes.items[0];
          setPedidoEmEdicao(pedido);
          setCarrinho(pedido.itens.map(item => ({
            produto_id: item.produto_id,
            produto_nome: item.produto_nome || '',
            preco_unitario: item.preco_unitario,
            quantidade_saida: item.quantidade_saida,
            valor_total: item.quantidade_saida * item.preco_unitario,
          })));
          toast({
            title: 'Pedido em Aberto Carregado',
            description: `O Pedido #${pedido.id} do ambulante ${pedido.ambulante_nome} foi carregado para edição (reforço).`,
          });
        } else {
          setPedidoEmEdicao(null);
          setCarrinho([]);
        }
      } catch (error) {
        toast({
          title: 'Erro ao carregar pedido em aberto',
          description: 'Não foi possível carregar o pedido em aberto para o ambulante selecionado.',
          variant: 'destructive',
        });
      }
    }
    fetchPedidoEmAberto();
  }, [selectedAmbulanteId]);

  const handleAddItem = (produto: Produto, quantidade: number) => {
    if (quantidade <= 0) return;

    setCarrinho(prevCarrinho => {
      const itemIndex = prevCarrinho.findIndex(item => item.produto_id === produto.id);

      if (itemIndex > -1) {
        const novoCarrinho = [...prevCarrinho];
        novoCarrinho[itemIndex].quantidade_saida += quantidade;
        novoCarrinho[itemIndex].valor_total = novoCarrinho[itemIndex].quantidade_saida * produto.preco;
        return novoCarrinho;
      } else {
        const novoItem: CarrinhoItem = {
          produto_id: produto.id,
          produto_nome: produto.nome,
          preco_unitario: produto.preco,
          quantidade_saida: quantidade,
          valor_total: produto.preco * quantidade,
        };
        return [...prevCarrinho, novoItem];
      }
    });
  };

  const handleUpdateItemQuantity = (produtoId: number, newQuantity: number) => {
    setCarrinho(prevCarrinho => {
      const produto = produtos.find(p => p.id === produtoId);
      if (!produto) return prevCarrinho;

      const novoCarrinho = prevCarrinho
        .map(item => {
          if (item.produto_id === produtoId) {
            return {
              ...item,
              quantidade_saida: newQuantity,
              valor_total: produto.preco * newQuantity,
            };
          }
          return item;
        })
        .filter(item => item.quantidade_saida > 0);

      return novoCarrinho;
    });
  };

  const totalPedido = useMemo(() => {
    return carrinho.reduce((sum, item) => sum + item.valor_total, 0);
  }, [carrinho]);

  const handleFinalizarSaida = async () => {
    if (!selectedAmbulanteId) {
      toast({
        title: 'Atenção',
        description: 'Selecione um ambulante para finalizar o pedido.',
        variant: 'destructive',
      });
      return;
    }

    if (carrinho.length === 0) {
      toast({
        title: 'Atenção',
        description: 'O carrinho está vazio.',
        variant: 'destructive',
      });
      return;
    }

    const payload: PedidoSaidaForm = {
      ambulante_id: Number(selectedAmbulanteId),
      itens_saida: carrinho.map(item => ({
        produto_id: item.produto_id,
        quantidade_saida: item.quantidade_saida,
      })),
    };

    setIsSubmitting(true);
    try {
      let pedidoId: number;

      if (pedidoEmEdicao) {
        // Atualizar pedido existente
        await apiService.updatePedidoSaida(pedidoEmEdicao.id, payload);
        pedidoId = pedidoEmEdicao.id;
        toast({
          title: 'Sucesso',
          description: `Pedido #${pedidoId} atualizado com sucesso!`,
        });
      } else {
        // Criar novo pedido
        const newPedido = await apiService.createPedidoSaida(payload);
        pedidoId = newPedido.id;
        toast({
          title: 'Sucesso',
          description: `Pedido de saída #${pedidoId} registrado com sucesso!`,
        });
      }
      
      // IMPRIMIR NOTA FISCAL (Requisito do Usuário)
      try {
        console.log(`[DEBUG] Iniciando impressão da nota de saída para pedido ${pedidoId}`);
        await apiService.imprimirNotaSaida(pedidoId);
        console.log('[DEBUG] Nota de saída impressa com sucesso');
      } catch (error) {
        console.error('[ERROR] Erro ao imprimir nota de saída:', error);
        toast({
          title: 'Nota Fiscal',
          description: 'Nota de saída gerada. Verifique seu navegador para download.',
          variant: 'default',
        });
      }

      // Limpar e recarregar
      setSelectedAmbulanteId(null);
      setCarrinho([]);
      setPedidoEmEdicao(null);
      // A lógica de recarregar pedidos em aberto para o ambulante selecionado está no useEffect
      
    } catch (error) {
      toast({
        title: 'Erro ao registrar saída',
        description: error instanceof Error ? error.message : 'Ocorreu um erro ao tentar enviar o pedido.',
        variant: 'destructive',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <MainLayout title="Registro de Saída (Totem)">
        <div className="flex justify-center items-center h-full">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout title="Registro de Saída (Totem)">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
        {/* Coluna de Produtos (Totem) */}
        <div className="lg:col-span-2 space-y-4 overflow-y-auto p-2">
          <h2 className="text-2xl font-bold">Produtos Disponíveis</h2>
          
          {/* Agrupa produtos por categoria na ordem especificada */}
          {(() => {
            const categoriaOrder = ['Kibon', 'Nestle', 'Gelo', 'Outros', 'Acessórios'];
            const produtosPorCategoria: { [key: string]: typeof produtos } = {};
            
            // Agrupa produtos por categoria
            produtos.forEach(produto => {
              const catNome = produto.categoria_nome || 'Sem Categoria';
              if (!produtosPorCategoria[catNome]) {
                produtosPorCategoria[catNome] = [];
              }
              produtosPorCategoria[catNome].push(produto);
            });
            
            // Ordena as categorias conforme especificado
            const categoriasOrdenadas = Object.keys(produtosPorCategoria).sort((a, b) => {
              const indexA = categoriaOrder.indexOf(a);
              const indexB = categoriaOrder.indexOf(b);
              if (indexA === -1) return 1;
              if (indexB === -1) return -1;
              return indexA - indexB;
            });
            
            return categoriasOrdenadas.map(categoria => (
              <div key={categoria}>
                <h3 className="text-xl font-semibold mb-3 pb-2 border-b-2 border-blue-500">
                  {categoria}
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {produtosPorCategoria[categoria].map(produto => (
              <Card key={produto.id} className="cursor-pointer hover:shadow-lg transition-shadow">
                <CardHeader className="p-3">
                  <CardTitle className="text-lg">{produto.nome}</CardTitle>
                </CardHeader>
                <CardContent className="p-3 pt-0">
                  <p className="text-sm text-muted-foreground">Estoque: {produto.estoque}</p>
                  <p className="text-xl font-semibold text-primary">R$ {produto.preco.toFixed(2)}</p>
                  {/* Mostra peso se o produto tiver (para Gelo Seco) */}
                  {(produto as any).peso && (produto as any).peso > 0 && (
                    <p className="text-sm text-blue-600 font-semibold">Peso/Un: {((produto as any).peso).toFixed(2)} kg</p>
                  )}
                  {/* Verifica se é produto por peso (kg) */}
                  {produto.nome.toLowerCase().includes('kg') || produto.nome.toLowerCase().includes('gelo') || ((produto as any).peso && (produto as any).peso > 0) ? (
                    <div className="mt-2">
                      <label className="text-xs text-muted-foreground">Quantidade (kg):</label>
                      <input
                        type="number"
                        step="0.001"
                        min="0"
                        max={produto.estoque}
                        value={carrinho.find(item => item.produto_id === produto.id)?.quantidade_saida || 0}
                        onChange={(e) => {
                          // Substitui vírgula por ponto para garantir que parseFloat funcione corretamente
                          const rawValue = e.target.value.replace(',', '.');
                          const valor = parseFloat(rawValue) || 0;
                          
                          // Garante que o valor não é negativo
                          const finalValue = Math.max(0, valor);

                          if (finalValue >= 0) {
                            handleUpdateItemQuantity(produto.id, finalValue);
                          }
                        }}
                        className="w-full px-2 py-1 border rounded text-center"
                        placeholder="0.000"
                      />
                    </div>
                  ) : (
                    <div className="flex items-center justify-between mt-2">
                      <Button
                        onClick={() => {
                          const atual = carrinho.find(i => i.produto_id === produto.id)?.quantidade_saida || 0;
                          handleUpdateItemQuantity(produto.id, Math.max(0, atual - 1));
                        }}
                        className="text-lg px-4 py-2 border rounded-md"
                        disabled={(carrinho.find(i => i.produto_id === produto.id)?.quantidade_saida || 0) <= 0}
                      >
                        -
                      </Button>
                      <span className="text-lg font-medium">
                        {carrinho.find(item => item.produto_id === produto.id)?.quantidade_saida || 0}
                      </span>
                      <Button
                        onClick={() => handleAddItem(produto, 1)}
                        className="text-lg px-4 py-2"
                      >
                        +
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
                  ))}
                </div>
              </div>
            ));
          })()}
        </div>

        {/* Coluna de Carrinho */}
        <Card className="lg:col-span-1 flex flex-col h-full">
          <CardHeader>
            <CardTitle>Carrinho de Saída</CardTitle>
          </CardHeader>
          <CardContent className="flex-grow flex flex-col">
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Ambulante</label>
              <Select onValueChange={value => setSelectedAmbulanteId(Number(value))} value={selectedAmbulanteId?.toString() || ''} disabled={isSubmitting}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione o Ambulante" />
                </SelectTrigger>
                <SelectContent>
                  {ambulantes.map(ambulante => (
                    <SelectItem key={ambulante.id} value={ambulante.id.toString()}>
                      {ambulante.nome}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex-grow overflow-y-auto space-y-2 border p-3 rounded-md">
              {carrinho.length === 0 ? (
                <p className="text-center text-muted-foreground">Nenhum item adicionado.</p>
              ) : (
                carrinho.map(item => (
                  <div key={item.produto_id} className="flex justify-between items-center border-b pb-2">
                    <div>
                      <p className="font-medium">{item.produto_nome}</p>
                      <p className="text-sm text-muted-foreground">
                        {item.quantidade_saida} x R$ {item.preco_unitario.toFixed(2)}
                      </p>
                    </div>
                    <p className="font-semibold">R$ {item.valor_total.toFixed(2)}</p>
                  </div>
                ))
              )}
            </div>

            <div className="mt-4 pt-4 border-t">
              <div className="flex justify-between text-xl font-bold mb-4">
                <span>Total:</span>
                <span>R$ {totalPedido.toFixed(2)}</span>
              </div>
              <Button
                onClick={handleFinalizarSaida}
                className="w-full py-6 text-lg"
                disabled={!selectedAmbulanteId || carrinho.length === 0 || isSubmitting}
              >
                {isSubmitting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                {pedidoEmEdicao ? `Atualizar Pedido #${pedidoEmEdicao.id}` : 'Registrar Saída'}
              </Button>
              {pedidoEmEdicao && (
                <Button
                  onClick={() => {
                    setPedidoEmEdicao(null);
                    setSelectedAmbulanteId(null);
                    setCarrinho([]);
                  }}
                  className="w-full mt-2 border rounded-md"
                >
                  Novo Pedido
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
