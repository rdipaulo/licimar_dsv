import React, { useState, useEffect, useMemo } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Pedido,
  ItemPedido,
  PedidoRetornoForm,
  PaginatedResponse,
} from '../../types';
import { api } from '../../services/api';
import { MainLayout } from '../../components/MainLayout';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { ScrollArea } from '../../components/ui/scroll-area';
import { Separator } from '../../components/ui/separator';
import { toast } from '../../components/ui/use-toast';
import { Loader2, Calculator, ListOrdered, CheckCircle } from 'lucide-react';
import { format } from 'date-fns';

// --- Schemas de Validação ---
const itemRetornoSchema = z.object({
  produto_id: z.number(),
  quantidade_retorno: z.number().min(0, 'A quantidade deve ser positiva.'),
});

const pedidoRetornoSchema = z.object({
  itens_retorno: z.array(itemRetornoSchema),
});

type PedidoRetornoFormData = z.infer<typeof pedidoRetornoSchema>;

// --- Componente Principal da Tela de Retorno ---
export const PedidosRetorno: React.FC = () => {
  const [pedidosEmAberto, setPedidosEmAberto] = useState<Pedido[]>([]);
  const [pedidoSelecionado, setPedidoSelecionado] = useState<Pedido | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [valorFinal, setValorFinal] = useState<number | null>(null);

  const {
    handleSubmit,
    control,
    setValue,
    watch,
    reset,
    formState: { errors },
  } = useForm<PedidoRetornoFormData>({
    resolver: zodResolver(pedidoRetornoSchema),
    defaultValues: {
      itens_retorno: [],
    },
  });

  const { fields, replace } = useFieldArray({
    control,
    name: 'itens_retorno',
  });

  const watchedItensRetorno = watch('itens_retorno');

  // Carregar pedidos em aberto
  const fetchPedidosEmAberto = async () => {
    try {
      const response = await api.get<any>('/pedidos', {
        params: { status: 'saida', per_page: 100 }, // Ajustar per_page conforme necessário
      });
      const pedidosData = response.data.items || response.data;
      setPedidosEmAberto(pedidosData);
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

  useEffect(() => {
    fetchPedidosEmAberto();
  }, []);

  // Quando um pedido é selecionado
  useEffect(() => {
    if (pedidoSelecionado) {
      const itensParaForm = pedidoSelecionado.itens.map(item => ({
        produto_id: item.produto_id,
        quantidade_retorno: item.quantidade_retorno || 0, // Inicializa com 0 ou valor existente
      }));
      replace(itensParaForm);
      setValorFinal(null); // Reseta o valor final ao selecionar novo pedido
    } else {
      replace([]);
    }
  }, [pedidoSelecionado, replace]);

  // Lógica para calcular quantidades vendidas e perdas (apenas visual)
  const itensComCalculo = useMemo(() => {
    if (!pedidoSelecionado) return [];

    return pedidoSelecionado.itens.map((itemOriginal, index) => {
      const itemRetorno = watchedItensRetorno.find(
        (item) => item.produto_id === itemOriginal.produto_id
      );
      const quantidadeRetorno = itemRetorno?.quantidade_retorno || 0;
      const quantidadeSaida = itemOriginal.quantidade_saida;
      const quantidadeVendida = Math.max(0, quantidadeSaida - quantidadeRetorno);
      const quantidadePerda = Math.max(0, quantidadeRetorno - quantidadeSaida); // Simplificado: se retornou mais do que saiu, é erro ou perda

      return {
        ...itemOriginal,
        quantidadeRetorno,
        quantidadeVendida,
        quantidadePerda,
        nome_produto: itemOriginal.produto_nome, // Assumindo que o Pedido retornado pela API tem o nome do produto
        preco_unitario: itemOriginal.preco_unitario, // Assumindo que o Pedido retornado pela API tem o preço
      };
    });
  }, [pedidoSelecionado, watchedItensRetorno]);

  // Submissão do formulário (Registro de Retorno e Cálculo)
  const onSubmit = async (data: PedidoRetornoFormData) => {
    if (!pedidoSelecionado) return;

    setIsSubmitting(true);
    try {
      const payload: PedidoRetornoForm = {
        itens: data.itens_retorno.map(item => ({
          produto_id: item.produto_id,
          quantidade_retorno: item.quantidade_retorno,
        })),
      };

      // Endpoint para registro de retorno e cálculo
      const response = await api.post<Pedido>(`/pedidos/${pedidoSelecionado.id}/retorno`, payload);

      const pedidoAtualizado = response.data.pedido || response.data;
      setValorFinal(pedidoAtualizado.total || 0);
      setPedidoSelecionado(pedidoAtualizado); // Atualiza o pedido com o status finalizado
      
      toast({
        title: 'Sucesso!',
        description: `Cálculo finalizado. Total a pagar: R$ ${pedidoAtualizado.total?.toFixed(2)}`,
      });

      // Recarrega a lista de pedidos em aberto
      await fetchPedidosEmAberto();
      
    } catch (error) {
      toast({
        title: 'Erro ao finalizar pedido',
        description: 'Ocorreu um erro ao tentar registrar o retorno e calcular o valor final.',
        variant: 'destructive',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSelectPedido = (pedido: Pedido) => {
    setPedidoSelecionado(pedido);
    setValorFinal(null);
  };

  if (isLoading) {
    return (
      <MainLayout title="Registro de Retorno/Cálculo">
        <div className="flex justify-center items-center h-64">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout title="Registro de Retorno/Cálculo">
      <div className="flex h-full space-x-4">
        {/* Coluna de Pedidos em Aberto */}
        <Card className="w-80 flex-shrink-0">
          <CardHeader>
            <CardTitle className="text-lg flex items-center">
              <ListOrdered className="h-5 w-5 mr-2" /> Pedidos em Aberto
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <ScrollArea className="h-[calc(100vh-200px)]">
              {pedidosEmAberto.length === 0 ? (
                <p className="p-4 text-sm text-muted-foreground">Nenhum pedido em aberto.</p>
              ) : (
                pedidosEmAberto.map(pedido => (
                  <div
                    key={pedido.id}
                    className={`p-4 border-b cursor-pointer hover:bg-accent ${
                      pedidoSelecionado?.id === pedido.id ? 'bg-primary/10 font-semibold' : ''
                    }`}
                    onClick={() => handleSelectPedido(pedido)}
                  >
                    <p className="text-sm">Pedido #{pedido.id}</p>
                    <p className="text-xs text-muted-foreground">{pedido.ambulante_nome}</p>
                    <p className="text-xs text-muted-foreground">
                      Saída: {format(new Date(pedido.data_operacao), 'dd/MM/yyyy HH:mm')}
                    </p>
                  </div>
                ))
              )}
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Coluna de Detalhes e Retorno */}
        <Card className="flex-1">
          <CardHeader>
            <CardTitle className="text-xl">
              {pedidoSelecionado ? `Detalhes do Pedido #${pedidoSelecionado.id}` : 'Selecione um Pedido'}
            </CardTitle>
            {pedidoSelecionado && (
              <p className="text-sm text-muted-foreground">
                Ambulante: {pedidoSelecionado.ambulante_nome} | Status: {pedidoSelecionado.status}
              </p>
            )}
          </CardHeader>
          <CardContent>
            {pedidoSelecionado && pedidoSelecionado.status !== 'finalizado' ? (
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <ScrollArea className="h-[calc(100vh-350px)] pr-4">
                  <div className="space-y-4">
                    {itensComCalculo.map((item, index) => (
                      <div key={item.produto_id} className="border p-3 rounded-lg">
                        <p className="font-semibold">{item.nome_produto}</p>
                        <div className="grid grid-cols-3 gap-4 mt-2">
                          <div>
                            <Label className="text-xs">Saída</Label>
                            <p className="font-medium">{item.quantidade_saida}</p>
                          </div>
                          <div>
                            <Label htmlFor={`retorno-${item.produto_id}`} className="text-xs">
                              Retorno
                            </Label>
                            <Input
                              id={`retorno-${item.produto_id}`}
                              type={item.nome_produto?.toLowerCase().includes('gelo seco') ? 'number' : 'number'}
                              step={item.nome_produto?.toLowerCase().includes('gelo seco') ? '0.1' : '1'}
                              min="0"
                              {...control.register(`itens_retorno.${index}.quantidade_retorno`, {
                                valueAsNumber: true,
                              })}
                              className="h-8"
                            />
                            {errors.itens_retorno?.[index]?.quantidade_retorno && (
                              <p className="text-xs text-red-500">
                                {errors.itens_retorno[index].quantidade_retorno.message}
                              </p>
                            )}
                          </div>
                          <div>
                            <Label className="text-xs">Vendido (Visual)</Label>
                            <p className="font-medium text-green-600">{item.quantidadeVendida}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>

                <Separator />

                <Button
                  type="submit"
                  className="w-full"
                  disabled={isSubmitting || itensComCalculo.length === 0}
                >
                  {isSubmitting ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <>
                      <Calculator className="mr-2 h-4 w-4" /> Registrar Retorno e Calcular
                    </>
                  )}
                </Button>
              </form>
            ) : pedidoSelecionado && pedidoSelecionado.status === 'finalizado' ? (
              <div className="text-center p-8 space-y-4">
                <CheckCircle className="h-12 w-12 text-green-500 mx-auto" />
                <h3 className="text-xl font-semibold">Pedido Finalizado</h3>
                <p className="text-lg">
                  Valor Total a Pagar: <span className="font-bold text-green-600">R$ {pedidoSelecionado.total?.toFixed(2)}</span>
                </p>
                <Button onClick={() => setPedidoSelecionado(null)}>Novo Cálculo</Button>
              </div>
            ) : (
              <p className="text-center text-muted-foreground p-8">
                Utilize a lista à esquerda para selecionar um pedido em aberto.
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
};

export default PedidosRetorno;
