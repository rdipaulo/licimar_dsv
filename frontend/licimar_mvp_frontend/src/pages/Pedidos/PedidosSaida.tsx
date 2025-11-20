// Caminho: src/pages/Pedidos/PedidosSaida.tsx

import { useState, useEffect, useMemo } from 'react';
import { MainLayout } from '../../components/MainLayout';
import { api } from '../../services/api';
import { Ambulante, Produto, ItemPedido } from '../../types';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { useToast } from '../../hooks/use-toast'; 
import { Loader2 } from 'lucide-react';

interface PedidoSaidaForm {
  ambulante_id: number;
  itens: {
    produto_id: number;
    quantidade_saida: number;
  }[];
}

export default function PedidosSaida() {
  const { toast } = useToast();
  const [ambulantes, setAmbulantes] = useState<Ambulante[]>([]);
  const [produtos, setProdutos] = useState<Produto[]>([]);
  const [selectedAmbulanteId, setSelectedAmbulanteId] = useState<number | null>(null);
  const [carrinho, setCarrinho] = useState<ItemPedido[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [ambulantesRes, produtosRes] = await Promise.all([
          api.get<Ambulante[]>('/ambulantes'),
          api.get<Produto[]>('/produtos'),
        ]);
        setAmbulantes(ambulantesRes.data);
        setProdutos(produtosRes.data);
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
  }, [toast]);

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
        const novoItem: ItemPedido = {
          produto_id: produto.id,
          produto_nome: produto.nome,
          preco_unitario: produto.preco,
          quantidade_saida: quantidade,
          quantidade_retorno: 0,
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
      itens: carrinho.map(item => ({
        produto_id: item.produto_id,
        quantidade_saida: item.quantidade_saida,
      })),
    };

    try {
      await api.post('/pedidos/saida', payload);
      toast({
        title: 'Sucesso',
        description: 'Pedido de saída registrado com sucesso!',
      });
      setSelectedAmbulanteId(null);
      setCarrinho([]);
    } catch (error) {
      toast({
        title: 'Erro ao registrar saída',
        description: 'Ocorreu um erro ao tentar enviar o pedido.',
        variant: 'destructive',
      });
    }
  };

  if (isLoading) {
    return (
      <MainLayout title="Registro de Saída (Totem)" description="Carregando dados...">
        <div className="flex justify-center items-center h-full">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout title="Registro de Saída (Totem)" description="Interface de autoatendimento para registro de produtos retirados por ambulantes.">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
        {/* Coluna de Produtos (Totem) */}
        <div className="lg:col-span-2 space-y-4 overflow-y-auto p-2">
          <h2 className="text-2xl font-bold">Produtos Disponíveis</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {produtos.map(produto => (
              <Card key={produto.id} className="cursor-pointer hover:shadow-lg transition-shadow">
                <CardHeader className="p-3">
                  <CardTitle className="text-lg">{produto.nome}</CardTitle>
                </CardHeader>
                <CardContent className="p-3 pt-0">
                  <p className="text-sm text-muted-foreground">Estoque: {produto.estoque}</p>
                  <p className="text-xl font-semibold text-primary">R$ {produto.preco.toFixed(2)}</p>
                  <div className="flex items-center justify-between mt-2">
                    <Button
                      size="sm"
                      onClick={() => handleAddItem(produto, 1)}
                      className="text-lg px-4 py-2"
                    >
                      +
                    </Button>
                    <span className="text-lg font-medium">
                      {carrinho.find(item => item.produto_id === produto.id)?.quantidade_saida || 0}
                    </span>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleUpdateItemQuantity(produto.id, (carrinho.find(item => item.produto_id === produto.id)?.quantidade_saida || 0) - 1)}
                      className="text-lg px-4 py-2"
                      disabled={!carrinho.find(item => item.produto_id === produto.id)}
                    >
                      -
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Coluna de Carrinho */}
        <Card className="lg:col-span-1 flex flex-col h-full">
          <CardHeader>
            <CardTitle>Carrinho de Saída</CardTitle>
          </CardHeader>
          <CardContent className="flex-grow flex flex-col">
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Ambulante</label>
              <Select onValueChange={value => setSelectedAmbulanteId(Number(value))} value={selectedAmbulanteId?.toString() || ''}>
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
                disabled={!selectedAmbulanteId || carrinho.length === 0}
              >
                Finalizar Saída
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
