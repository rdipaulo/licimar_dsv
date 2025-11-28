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
import { Ambulante } from '../types';
import { toast } from 'sonner';

/**
 * Página de Ambulantes
 * Gerenciamento completo de ambulantes (CRUD)
 */
const AmbulantesPag: React.FC = () => {
  const [ambulantes, setAmbulantes] = useState<Ambulante[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const [showModal, setShowModal] = useState(false);
  const [editingAmbulante, setEditingAmbulante] = useState<Ambulante | null>(null);
  const [formData, setFormData] = useState({
    nome: '',
    email: '',
    telefone: '',
    cpf: '',
    endereco: '',
    divida_acumulada: 0,
  });

  // Carrega ambulantes da API
  useEffect(() => {
    loadAmbulantes();
  }, [page, searchTerm]);

  const loadAmbulantes = async () => {
    try {
      setLoading(true);
      const response = await apiService.getAmbulantes({
        page,
        per_page: 10,
        search: searchTerm || undefined,
      });
      setAmbulantes(response.items || response.data || []);
    } catch (error) {
      toast.error('Erro ao carregar ambulantes');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = (ambulante?: Ambulante) => {
    if (ambulante) {
      setEditingAmbulante(ambulante);
      setFormData({
        nome: ambulante.nome,
        email: ambulante.email || '',
        telefone: ambulante.telefone || '',
        cpf: ambulante.cpf || '',
        endereco: ambulante.endereco || '',
        divida_acumulada: (ambulante as any).divida_acumulada || 0,
      });
    } else {
      setEditingAmbulante(null);
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
    setEditingAmbulante(null);
    setFormData({
      nome: '',
      email: '',
      telefone: '',
      cpf: '',
      endereco: '',
      divida_acumulada: 0,
    });
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
      if (editingAmbulante) {
        payload.status = payload.status || 'ativo';
      } else {
        payload.status = 'ativo';
      }

      console.log('[Ambulantes] Payload:', payload);

      if (editingAmbulante) {
        await apiService.updateAmbulante(editingAmbulante.id, payload);
        toast.success('Ambulante atualizado com sucesso!');
      } else {
        await apiService.createAmbulante(payload);
        toast.success('Ambulante criado com sucesso!');
      }

      handleCloseModal();
      loadAmbulantes();
    } catch (error: any) {
      console.error('Erro ao salvar ambulante:', error);
      const errorMsg = error.response?.data?.message || error.message || 'Erro ao salvar ambulante';
      toast.error(errorMsg);
    }
  };

  const handleToggleStatus = async (ambulante: Ambulante) => {
    const newStatus = ambulante.status === 'ativo' ? 'inativo' : 'ativo';
    const action = newStatus === 'ativo' ? 'ativar' : 'desativar';

    if (!window.confirm(`Tem certeza que deseja ${action} ${ambulante.nome}?`)) {
      return;
    }

    try {
      await apiService.updateAmbulante(ambulante.id, { status: newStatus });
      toast.success(`Ambulante ${action}ado com sucesso`);
      loadAmbulantes();
    } catch (error: any) {
      toast.error(error.response?.data?.message || `Erro ao ${action} ambulante`);
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
    <MainLayout title="Ambulantes">
      <div className="space-y-6">
        {/* Header com Botão de Novo */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Gestão de Ambulantes</h2>
            <p className="text-sm text-gray-600">Cadastro e gerenciamento de vendedores ambulantes</p>
          </div>
          <Button className="bg-indigo-600 hover:bg-indigo-700" onClick={() => handleOpenModal()}>
            <Plus size={18} className="mr-2" />
            Novo Ambulante
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

        {/* Tabela de Ambulantes */}
        <Card>
          <CardHeader>
            <CardTitle>Lista de Ambulantes</CardTitle>
            <CardDescription>
              {ambulantes.length} ambulante(s) encontrado(s)
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
              </div>
            ) : ambulantes.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>Nenhum ambulante encontrado</p>
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
                    {ambulantes.map((ambulante) => (
                      <TableRow key={ambulante.id} className="hover:bg-gray-50">
                        <TableCell className="font-medium">{ambulante.nome}</TableCell>
                        <TableCell>{ambulante.email || '-'}</TableCell>
                        <TableCell>{ambulante.telefone || '-'}</TableCell>
                        <TableCell>{ambulante.cpf || '-'}</TableCell>
                        <TableCell>
                          <span className={((ambulante as any).divida_acumulada || 0) > 0 ? 'text-red-600 font-semibold' : 'text-gray-500'}>
                            R$ {(((ambulante as any).divida_acumulada || 0).toFixed(2))}
                          </span>
                        </TableCell>
                        <TableCell>{getStatusBadge(ambulante.status)}</TableCell>
                        <TableCell className="text-right">
                          <div className="flex items-center justify-end space-x-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                              onClick={() => handleOpenModal(ambulante)}
                              title="Editar"
                            >
                              <Edit size={16} />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleToggleStatus(ambulante)}
                              title={ambulante.status === 'ativo' ? "Desativar" : "Ativar"}
                            >
                              {ambulante.status === 'ativo' ? (
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
              {editingAmbulante ? 'Editar Ambulante' : 'Novo Ambulante'}
            </DialogTitle>
            <DialogDescription>
              {editingAmbulante
                ? 'Atualize as informações do ambulante'
                : 'Preencha os dados do novo ambulante'}
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
                {editingAmbulante ? 'Atualizar' : 'Criar'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </MainLayout>
  );
};

export default AmbulantesPag;
