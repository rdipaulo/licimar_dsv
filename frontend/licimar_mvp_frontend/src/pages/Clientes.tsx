import React, { useState, useEffect } from 'react';
import { Plus, Edit, ToggleLeft, ToggleRight, Search } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../components/ui/dialog';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import MainLayout from '../components/MainLayout';
import { apiService } from '../services/api';
import { cliente } from '../types';
import { toast } from 'sonner';

/**
 * Página de clientes
 * Gerenciamento completo de clientes (CRUD)
 */
const clientesPag: React.FC = () => {
  const [clientes, setclientes] = useState<cliente[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const [showModal, setShowModal] = useState(false);
  const [editingcliente, setEditingcliente] = useState<cliente | null>(null);
  const [formData, setFormData] = useState({
    nome: '',
    email: '',
    telefone: '',
    cpf: '',
    endereco: '',
    divida_acumulada: 0,
  });

  // Carrega clientes da API
  useEffect(() => {
    loadclientes();
  }, [page, searchTerm]);

  const loadclientes = async () => {
    try {
      setLoading(true);
      const response = await apiService.getclientes({
        page,
        per_page: 10,
        search: searchTerm || undefined,
      });
      setclientes(response.items || response.data || []);
    } catch (error) {
      toast.error('Erro ao carregar clientes');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = (cliente?: cliente) => {
    if (cliente) {
      setEditingcliente(cliente);
      setFormData({
        nome: cliente.nome,
        email: cliente.email || '',
        telefone: cliente.telefone || '',
        cpf: cliente.cpf || '',
        endereco: cliente.endereco || '',
        divida_acumulada: (cliente as any).divida_acumulada || 0,
      });
    } else {
      setEditingcliente(null);
      setFormData({
        nome: '',
        email: '',
        telefone: '',
        cpf: '',
        endereco: '',
        divida_acumulada: 0,
      });
    }
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingcliente(null);
    setFormData({
      nome: '',
      email: '',
      telefone: '',
      cpf: '',
      endereco: '',
      divida_acumulada: 0,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.nome.trim()) {
      toast.error('Nome é obrigatório');
      return;
    }

    try {
      const payload: any = {
        nome: formData.nome.trim(),
      };

      // Adiciona campos opcionais apenas se preenchidos
      if (formData.email.trim()) payload.email = formData.email.trim();
      if (formData.telefone.trim()) payload.telefone = formData.telefone.trim();
      if (formData.cpf.trim()) payload.cpf = formData.cpf.trim();
      if (formData.endereco.trim()) payload.endereco = formData.endereco.trim();
      
      // Apenas adicionar status se não estiver criando
      if (editingcliente) {
        payload.status = payload.status || 'ativo';
      } else {
        payload.status = 'ativo';
      }

      console.log('[clientes] Payload:', payload);

      if (editingcliente) {
        await apiService.updatecliente(editingcliente.id, payload);
        toast.success('cliente atualizado com sucesso!');
      } else {
        await apiService.createcliente(payload);
        toast.success('cliente criado com sucesso!');
      }

      handleCloseModal();
      loadclientes();
    } catch (error: any) {
      console.error('Erro ao salvar cliente:', error);
      const errorMsg = error.response?.data?.message || error.message || 'Erro ao salvar cliente';
      toast.error(errorMsg);
    }
  };

  const handleToggleStatus = async (cliente: cliente) => {
    const newStatus = cliente.status === 'ativo' ? 'inativo' : 'ativo';
    const action = newStatus === 'ativo' ? 'ativar' : 'desativar';

    if (!window.confirm(`Tem certeza que deseja ${action} ${cliente.nome}?`)) {
      return;
    }

    try {
      await apiService.updatecliente(cliente.id, { status: newStatus });
      toast.success(`cliente ${action}ado com sucesso`);
      loadclientes();
    } catch (error: any) {
      toast.error(error.response?.data?.message || `Erro ao ${action} cliente`);
      console.error(error);
    }
  };

  const getStatusBadge = (status: string) => {
    const baseClass = 'px-2 py-1 rounded text-xs font-medium';
    if (status === 'ativo') {
      return <span className={`${baseClass} bg-green-100 text-green-800`}>Ativo</span>;
    }
    return <span className={`${baseClass} bg-red-100 text-red-800`}>Inativo</span>;
  };

  return (
    <MainLayout title="clientes">
      <div className="space-y-6">
        {/* Header com Botão de Novo */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Gestão de clientes</h2>
            <p className="text-sm text-gray-600">Cadastro e gerenciamento de vendedores clientes</p>
          </div>
          <Button className="bg-indigo-600 hover:bg-indigo-700" onClick={() => handleOpenModal()}>
            <Plus size={18} className="mr-2" />
            Novo cliente
          </Button>
        </div>

        {/* Barra de Pesquisa */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Filtros</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              <Search size={18} className="text-gray-400" />
              <Input
                placeholder="Pesquisar por nome, email ou telefone..."
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setPage(1);
                }}
                className="flex-1"
              />
            </div>
          </CardContent>
        </Card>

        {/* Tabela de clientes */}
        <Card>
          <CardHeader>
            <CardTitle>Lista de clientes</CardTitle>
            <CardDescription>
              {clientes.length} cliente(s) encontrado(s)
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
              </div>
            ) : clientes.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>Nenhum cliente encontrado</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-gray-50">
                      <TableHead>Nome</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Telefone</TableHead>
                      <TableHead>CPF</TableHead>
                      <TableHead>Dívida Acumulada</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Ações</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {clientes.map((cliente) => (
                      <TableRow key={cliente.id} className="hover:bg-gray-50">
                        <TableCell className="font-medium">{cliente.nome}</TableCell>
                        <TableCell>{cliente.email || '-'}</TableCell>
                        <TableCell>{cliente.telefone || '-'}</TableCell>
                        <TableCell>{cliente.cpf || '-'}</TableCell>
                        <TableCell>
                          <span className={((cliente as any).divida_acumulada || 0) > 0 ? 'text-red-600 font-semibold' : 'text-gray-500'}>
                            R$ {(((cliente as any).divida_acumulada || 0).toFixed(2))}
                          </span>
                        </TableCell>
                        <TableCell>{getStatusBadge(cliente.status)}</TableCell>
                        <TableCell className="text-right">
                          <div className="flex items-center justify-end space-x-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                              onClick={() => handleOpenModal(cliente)}
                              title="Editar"
                            >
                              <Edit size={16} />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleToggleStatus(cliente)}
                              title={cliente.status === 'ativo' ? "Desativar" : "Ativar"}
                            >
                              {cliente.status === 'ativo' ? (
                                <ToggleRight className="h-4 w-4 text-green-500" />
                              ) : (
                                <ToggleLeft className="h-4 w-4 text-gray-400" />
                              )}
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Dialog open={showModal} onOpenChange={setShowModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>
              {editingcliente ? 'Editar cliente' : 'Novo cliente'}
            </DialogTitle>
            <DialogDescription>
              {editingcliente
                ? 'Atualize as informações do cliente'
                : 'Preencha os dados do novo cliente'}
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

            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="telefone">Telefone</Label>
                <Input
                  id="telefone"
                  value={formData.telefone}
                  onChange={(e) =>
                    setFormData({ ...formData, telefone: e.target.value })
                  }
                />
              </div>

              <div>
                <Label htmlFor="cpf">CPF</Label>
                <Input
                  id="cpf"
                  value={formData.cpf}
                  onChange={(e) =>
                    setFormData({ ...formData, cpf: e.target.value })
                  }
                />
              </div>
            </div>

            <div>
              <Label htmlFor="endereco">Endereço</Label>
              <Input
                id="endereco"
                value={formData.endereco}
                onChange={(e) =>
                  setFormData({ ...formData, endereco: e.target.value })
                }
              />
            </div>

            <div>
              <Label htmlFor="divida_acumulada">Dívida Acumulada (R$)</Label>
              <Input
                id="divida_acumulada"
                type="number"
                step="0.01"
                value={formData.divida_acumulada}
                onChange={(e) =>
                  setFormData({ ...formData, divida_acumulada: parseFloat(e.target.value) || 0 })
                }
              />
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={handleCloseModal}>
                Cancelar
              </Button>
              <Button type="submit">
                {editingcliente ? 'Atualizar' : 'Criar'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </MainLayout>
  );
};

export default clientesPag;
