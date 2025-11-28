import React, { useState, useEffect } from 'react';
import { Plus, Edit, ToggleLeft, ToggleRight, Search, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { apiService as api } from '@/services/api';
import { toast } from 'sonner';

interface Produto {
  id: number;
  nome: string;
  preco: number;
  estoque: number;
  categoria_id: number | null;
  categoria_nome: string | null;
  descricao: string | null;
  estoque_minimo: number;
  estoque_baixo: boolean;
  active: boolean;
  peso?: number;
}

interface Categoria {
  id: number;
  nome: string;
  active: boolean;
}

const Produtos: React.FC = () => {
  const [produtos, setProdutos] = useState<Produto[]>([]);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [showInactive, setShowInactive] = useState(false);
  const [editingProduto, setEditingProduto] = useState<Produto | null>(null);
  const [formData, setFormData] = useState({
    nome: '',
    preco: '',
    estoque: '',
    categoria_id: '',
    descricao: '',
    estoque_minimo: '10',
    peso: '0',
  });

  useEffect(() => {
    loadProdutos();
    loadCategorias();
  }, [showInactive]);

  const loadProdutos = async () => {
    try {
      setLoading(true);
      const response = await api.getProdutos({
        page: 1,
        per_page: 1000,
        active_only: !showInactive
      });
      setProdutos(response.items || response.data || []);
    } catch (error) {
      console.error('Erro ao carregar produtos:', error);
      toast.error('Erro ao carregar produtos');
    } finally {
      setLoading(false);
    }
  };

  const loadCategorias = async () => {
    try {
      const response = await api.getCategorias({
        page: 1,
        per_page: 100
      });
      setCategorias(response.items || response.data || []);
      console.log('[Produtos] Categorias carregadas:', response.items || response.data);
    } catch (error) {
      console.error('Erro ao carregar categorias:', error);
      toast.error('Erro ao carregar categorias');
    }
  };

  const handleOpenModal = (produto?: Produto) => {
    if (produto) {
      setEditingProduto(produto);
      setFormData({
        nome: produto.nome,
        preco: produto.preco.toString(),
        estoque: produto.estoque.toString(),
        categoria_id: produto.categoria_id?.toString() || '',
        descricao: produto.descricao || '',
        estoque_minimo: produto.estoque_minimo.toString(),
        peso: (produto.peso || 0).toString(),
      });
    } else {
      setEditingProduto(null);
      setFormData({
        nome: '',
        preco: '',
        estoque: '',
        categoria_id: '',
        descricao: '',
        estoque_minimo: '10',
        peso: '0',
      });
    }
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingProduto(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const payload = {
        nome: formData.nome,
        preco: parseFloat(formData.preco),
        estoque: parseInt(formData.estoque),
        categoria_id: formData.categoria_id ? parseInt(formData.categoria_id) : null,
        descricao: formData.descricao || null,
        estoque_minimo: parseInt(formData.estoque_minimo),
        peso: parseFloat(formData.peso) || 0,
      };

      if (editingProduto) {
        await api.updateProduto(editingProduto.id, payload);
        toast.success('Produto atualizado com sucesso!');
      } else {
        await api.createProduto(payload);
        toast.success('Produto criado com sucesso!');
      }

      handleCloseModal();
      loadProdutos();
    } catch (error: any) {
      console.error('Erro ao salvar produto:', error);
      toast.error(error.response?.data?.message || error.message || 'Erro ao salvar produto');
    }
  };

  const handleToggleStatus = async (produto: Produto) => {
    const newStatus = !produto.active;
    const action = newStatus ? 'ativar' : 'desativar';
    
    if (!confirm(`Deseja realmente ${action} o produto "${produto.nome}"?`)) {
      return;
    }

    try {
      await api.updateProduto(produto.id, { active: newStatus });
      toast.success(`Produto ${action}ado com sucesso!`);
      loadProdutos();
    } catch (error: any) {
      console.error(`Erro ao ${action} produto:`, error);
      toast.error(error.response?.data?.message || `Erro ao ${action} produto`);
    }
  };

  const filteredProdutos = produtos.filter((produto) =>
    produto.nome.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Gerenciamento de Produtos</h1>
        <Button onClick={() => handleOpenModal()}>
          <Plus className="mr-2 h-4 w-4" />
          Novo Produto
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Produtos Cadastrados</CardTitle>
          <div className="flex items-center space-x-4 mt-4">
            <div className="flex items-center space-x-2 flex-1">
              <Search className="h-4 w-4 text-gray-400" />
              <Input
                placeholder="Buscar produto..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="max-w-sm"
              />
            </div>
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="showInactive"
                checked={showInactive}
                onChange={(e) => setShowInactive(e.target.checked)}
                className="rounded"
              />
              <label htmlFor="showInactive" className="text-sm text-gray-600 cursor-pointer">
                Mostrar inativos
              </label>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Carregando produtos...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nome</TableHead>
                  <TableHead>Categoria</TableHead>
                  <TableHead className="text-right">Preço</TableHead>
                  <TableHead className="text-right">Estoque</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredProdutos.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8 text-gray-500">
                      Nenhum produto encontrado
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredProdutos.map((produto) => (
                    <TableRow key={produto.id}>
                      <TableCell className="font-medium">
                        {produto.nome}
                        {produto.estoque_baixo && (
                          <AlertTriangle className="inline ml-2 h-4 w-4 text-yellow-500" />
                        )}
                      </TableCell>
                      <TableCell>{produto.categoria_nome || '-'}</TableCell>
                      <TableCell className="text-right">
                        {formatCurrency(produto.preco)}
                      </TableCell>
                      <TableCell className="text-right">
                        <span
                          className={
                            produto.estoque_baixo
                              ? 'text-yellow-600 font-semibold'
                              : ''
                          }
                        >
                          {produto.estoque}
                        </span>
                      </TableCell>
                      <TableCell>
                        <Badge variant={produto.active ? 'default' : 'secondary'}>
                          {produto.active ? 'Ativo' : 'Inativo'}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end space-x-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleOpenModal(produto)}
                            title="Editar"
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleToggleStatus(produto)}
                            title={produto.active ? "Desativar" : "Ativar"}
                          >
                            {produto.active ? (
                              <ToggleRight className="h-4 w-4 text-green-500" />
                            ) : (
                              <ToggleLeft className="h-4 w-4 text-gray-400" />
                            )}
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Dialog open={showModal} onOpenChange={setShowModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>
              {editingProduto ? 'Editar Produto' : 'Novo Produto'}
            </DialogTitle>
            <DialogDescription>
              {editingProduto
                ? 'Atualize as informações do produto'
                : 'Preencha os dados do novo produto'}
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="nome">Nome *</Label>
              <Input
                id="nome"
                value={formData.nome}
                onChange={(e) =>
                  setFormData({ ...formData, nome: e.target.value })
                }
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="preco">Preço (R$) *</Label>
                <Input
                  id="preco"
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.preco}
                  onChange={(e) =>
                    setFormData({ ...formData, preco: e.target.value })
                  }
                  required
                />
              </div>

              <div>
                <Label htmlFor="estoque">Estoque *</Label>
                <Input
                  id="estoque"
                  type="number"
                  min="0"
                  value={formData.estoque}
                  onChange={(e) =>
                    setFormData({ ...formData, estoque: e.target.value })
                  }
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="categoria">Categoria</Label>
                <select
                  id="categoria"
                  className="w-full px-3 py-2 border rounded-md"
                  value={formData.categoria_id}
                  onChange={(e) =>
                    setFormData({ ...formData, categoria_id: e.target.value })
                  }
                >
                  <option value="">Selecione...</option>
                  {categorias && categorias.length > 0 ? (
                    categorias
                      .filter((c) => c.active !== false)
                      .map((categoria) => (
                        <option key={categoria.id} value={categoria.id}>
                          {categoria.nome}
                        </option>
                      ))
                  ) : (
                    <option disabled>Nenhuma categoria disponível</option>
                  )}
                </select>
              </div>

              <div>
                <Label htmlFor="estoque_minimo">Estoque Mínimo</Label>
                <Input
                  id="estoque_minimo"
                  type="number"
                  min="0"
                  value={formData.estoque_minimo}
                  onChange={(e) =>
                    setFormData({ ...formData, estoque_minimo: e.target.value })
                  }
                />
              </div>

              <div>
                <Label htmlFor="peso">Peso (kg) - Para produtos como Gelo Seco</Label>
                <Input
                  id="peso"
                  type="number"
                  step="0.1"
                  min="0"
                  value={formData.peso}
                  onChange={(e) =>
                    setFormData({ ...formData, peso: e.target.value })
                  }
                  placeholder="Ex: 1.5 ou 1.7"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="descricao">Descrição</Label>
              <textarea
                id="descricao"
                className="w-full px-3 py-2 border rounded-md"
                rows={3}
                value={formData.descricao}
                onChange={(e) =>
                  setFormData({ ...formData, descricao: e.target.value })
                }
              />
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={handleCloseModal}>
                Cancelar
              </Button>
              <Button type="submit">
                {editingProduto ? 'Atualizar' : 'Criar'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Produtos;
