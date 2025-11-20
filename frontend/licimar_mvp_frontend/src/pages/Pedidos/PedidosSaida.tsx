import React, { useState, useEffect, useMemo } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Ambulante,
  Produto,
  PedidoSaidaForm,
  ItemPedido,
} from '../../types';
import { api } from '../../services/api';
import { MainLayout } from '../../components/MainLayout';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { ScrollArea } from '../../components/ui/scroll-area';
import { Separator } from '../../components/ui/separator';
import { toast } from '../../components/ui/use-toast';
import { Loader2, ShoppingCart, User, X } from 'lucide-react';

// --- Schemas de Validação ---
const itemSaidaSchema = z.object({
  produto_id: z.number(),
  quantidade_saida: z.number().min(0, 'A quantidade deve ser positiva.'),
});

const pedidoSaidaSchema = z.object({
  ambulante_id: z.number().min(1, 'Selecione um ambulante.'),
  itens_saida: z.array(itemSaidaSchema).min(1, 'Adicione pelo menos um item ao pedido.'),
  observacoes: z.string().optional(),
});

type PedidoSaidaFormData = z.infer<typeof pedidoSaidaSchema>;

// --- Componente de Card de Produto (Totem) ---
interface ProdutoCardProps {
  produto: Produto;
  onQuantityChange: (produtoId: number, quantity: number) => void;
  currentQuantity: number;
}

const ProdutoCard: React.FC<ProdutoCardProps> = ({
  produto,
  onQuantityChange,
  currentQuantity,
}) => {
  const isGeloSeco = produto.nome.toLowerCase().includes('gelo seco');
  const [quantity, setQuantity] = useState(currentQuantity);

  useEffect(() => {
    setQuantity(currentQuantity);
  }, [currentQuantity]);

  const handleIncrement = () => {
    const newQuantity = isGeloSeco ? quantity + 0.1 : quantity + 1;
    setQuantity(newQuantity);
    onQuantityChange(produto.id, newQuantity);
  };

  const handleDecrement = () => {
    if (quantity > 0) {
      const newQuantity = isGeloSeco ? Math.max(0, quantity - 0.1) : Math.max(0, quantity - 1);
      setQuantity(newQuantity);
      onQuantityChange(produto.id, newQuantity);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = isGeloSeco ? parseFloat(e.target.value) : parseInt(e.target.value, 10);
    if (!isNaN(value) && value >= 0) {
      setQuantity(value);
      onQuantityChange(produto.id, value);
    } else if (e.target.value === '') {
      setQuantity(0);
      onQuantityChange(produto.id, 0);
    }
  };

  return (
    <Card className="flex flex-col justify-between h-full shadow-lg hover:shadow-xl transition-shadow">
      <CardHeader className="p-3 pb-1">
        <CardTitle className="text-sm font-bold truncate">{produto.nome}</CardTitle>
        <p className="text-xs text-muted-foreground">R$ {produto.preco.toFixed(2)}</p>
      </CardHeader>
      <CardContent className="p-3 pt-1">
        <div className="flex items-center justify-between space-x-2">
          <Button
            variant="outline"
            size="icon"
            onClick={handleDecrement}
            disabled={quantity <= 0}
            className="h-8 w-8"
          >
            -
          </Button>
          <Input
            type={isGeloSeco ? 'number' : 'text'}
            step={isGeloSeco ? '0.1' : '1'}
            value={quantity === 0 ? '' : quantity.toFixed(isGeloSeco ? 1 : 0)}
            onChange={handleInputChange}
            className="text-center h-8 w-16"
            placeholder="0"
          />
          <Button variant="outline" size="icon" onClick={handleIncrement} className="h-8 w-8">
            +
          </Button>
        </div>
        {quantity > 0 && (
          <p className="text-xs text-right mt-1 font-medium text-primary">
            Total: R$ {(quantity * produto.preco).toFixed(2)}
          </p>
        )}
      </CardContent>
    </Card>
  );
};

// --- Componente Principal da Tela de Saída ---
export const PedidosSaida: React.FC = () => {
  const [ambulantes, setAmbulantes] = useState<Ambulante[]>([]);
  const [produtos, setProdutos] = useState<Produto[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    handleSubmit,
    control,
    setValue,
    watch,
    reset,
    formState: { errors },
  } = useForm<PedidoSaidaFormData>({
    resolver: zodResolver(pedidoSaidaSchema),
    defaultValues: {
      ambulante_id: 0,
      itens_saida: [],
      observacoes: '',
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'itens_saida',
  });

  const watchedItens = watch('itens_saida');
  const watchedAmbulanteId = watch('ambulante_id');

  // Carregar dados iniciais
  useEffect(() => {
    const fetchData = async () => {
      try {
      const [ambulantesRes, produtosRes] = await Promise.all([
        api.get<any>('/ambulantes'),
        api.get<any>('/produtos'),
      ]);
      const ambulantesData = ambulantesRes.data.items || ambulantesRes.data;
      const produtosData = produtosRes.data.items || produtosRes.data;
        setAmbulantes(ambulantesData.filter((a: any) => a.status === 'ativo'));
        setProdutos(produtosData.filter((p: any) => p.active));
      } catch (error) {
        toast({
          title: 'Erro ao carregar dados',
          description: 'Não foi possível carregar a lista de ambulantes e produtos.',
          variant: 'destructive',
        });
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  // Lógica para atualizar o array de itens_saida
  const handleQuantityChange = (produtoId: number, quantity: number) => {
    const existingIndex = watchedItens.findIndex(item => item.produto_id === produtoId);

    if (quantity > 0) {
      if (existingIndex >= 0) {
        // Atualiza a quantidade
        setValue(`itens_saida.${existingIndex}.quantidade_saida`, quantity, { shouldValidate: true });
      } else {
        // Adiciona novo item
        append({ produto_id: produtoId, quantidade_saida: quantity });
      }
    } else {
      if (existingIndex >= 0) {
        // Remove item se a quantidade for 0
        remove(existingIndex);
      }
    }
  };

  // Calcula o resumo do carrinho
  const carrinhoResumo = useMemo(() => {
    let totalItens = 0;
    let valorTotal = 0;

    const itensComDetalhes = watchedItens.map(item => {
      const produto = produtos.find(p => p.id === item.produto_id);
      if (produto) {
        totalItens += 1;
        valorTotal += item.quantidade_saida * produto.preco;
        return {
          ...item,
          nome: produto.nome,
          preco: produto.preco,
        };
      }
      return null;
    }).filter(item => item !== null);

    return { itens: itensComDetalhes, totalItens, valorTotal };
  }, [watchedItens, produtos]);

  // Submissão do formulário
  const onSubmit = async (data: PedidoSaidaFormData) => {
    setIsSubmitting(true);
    try {
      const payload: PedidoSaidaForm = {
        ambulante_id: data.ambulante_id,
        itens_saida: data.itens_saida.map(item => ({
          produto_id: item.produto_id,
          quantidade_saida: item.quantidade_saida,
        })),
        observacoes: data.observacoes,
      };

      await api.post('/pedidos/saida', payload);

      toast({
        title: 'Sucesso!',
        description: 'Pedido de saída registrado com sucesso.',
      });

      // Limpar formulário
      reset({
        ambulante_id: 0,
        itens_saida: [],
        observacoes: '',
      });
    } catch (error) {
      toast({
        title: 'Erro ao registrar pedido',
        description: 'Ocorreu um erro ao tentar salvar o pedido de saída.',
        variant: 'destructive',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <MainLayout title="Registro de Saída (Totem)">
        <div className="flex justify-center items-center h-64">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      </MainLayout>
    );
  }

  const ambulanteSelecionado = ambulantes.find(a => a.id === watchedAmbulanteId);

  return (
    <MainLayout title="Registro de Saída (Totem)">
      <form onSubmit={handleSubmit(onSubmit)} className="flex h-full space-x-4">
        {/* Coluna de Seleção de Produtos (Totem) */}
        <div className="flex-1">
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Produtos Disponíveis</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[calc(100vh-250px)] pr-4">
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {produtos.map(produto => (
                    <ProdutoCard
                      key={produto.id}
                      produto={produto}
                      currentQuantity={
                        watchedItens.find(item => item.produto_id === produto.id)?.quantidade_saida || 0
                      }
                      onQuantityChange={handleQuantityChange}
                    />
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>

        {/* Coluna de Resumo do Pedido (Carrinho) */}
        <div className="w-80 flex flex-col space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                <User className="h-4 w-4 mr-2 inline" /> Ambulante
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Label htmlFor="ambulante_id">Selecione o Ambulante</Label>
                <Select
                  onValueChange={value => setValue('ambulante_id', parseInt(value, 10), { shouldValidate: true })}
                  value={watchedAmbulanteId > 0 ? String(watchedAmbulanteId) : ''}
                >
                  <SelectTrigger id="ambulante_id">
                    <SelectValue placeholder="Selecione..." />
                  </SelectTrigger>
                  <SelectContent>
                    {ambulantes.map(ambulante => (
                      <SelectItem key={ambulante.id} value={String(ambulante.id)}>
                        {ambulante.nome}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.ambulante_id && (
                  <p className="text-xs text-red-500">{errors.ambulante_id.message}</p>
                )}
              </div>
            </CardContent>
          </Card>

          <Card className="flex-1">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                <ShoppingCart className="h-4 w-4 mr-2 inline" /> Resumo do Pedido
              </CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col h-full">
              <ScrollArea className="flex-1 pr-4">
                {carrinhoResumo.itens.length === 0 ? (
                  <p className="text-sm text-muted-foreground">Nenhum item adicionado.</p>
                ) : (
                  <div className="space-y-2">
                    {carrinhoResumo.itens.map(item => (
                      <div key={item.produto_id} className="flex justify-between items-center text-sm">
                        <span className="truncate">
                          {item.quantidade_saida.toFixed(item.nome.toLowerCase().includes('gelo seco') ? 1 : 0)}x {item.nome}
                        </span>
                        <span className="font-semibold">R$ {(item.quantidade_saida * item.preco).toFixed(2)}</span>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6"
                          onClick={() => handleQuantityChange(item.produto_id, 0)}
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </ScrollArea>
              <Separator className="my-4" />
              <div className="space-y-2">
                <div className="flex justify-between font-bold text-lg">
                  <span>Total:</span>
                  <span>R$ {carrinhoResumo.valorTotal.toFixed(2)}</span>
                </div>
                {errors.itens_saida && (
                  <p className="text-xs text-red-500">{errors.itens_saida.message}</p>
                )}
                <Button
                  type="submit"
                  className="w-full"
                  disabled={isSubmitting || carrinhoResumo.itens.length === 0 || !ambulanteSelecionado}
                >
                  {isSubmitting ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    'Finalizar Pedido de Saída'
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </form>
    </MainLayout>
  );
};

export default PedidosSaida;
