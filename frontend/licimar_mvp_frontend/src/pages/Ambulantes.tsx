import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Search } from 'lucide-react';
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
      setAmbulantes(response.items);
    } catch (error) {
      toast.error('Erro ao carregar ambulantes');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Tem certeza que deseja deletar este ambulante?')) {
      return;
    }

    try {
      await apiService.deleteAmbulante(id);
      toast.success('Ambulante deletado com sucesso');
      loadAmbulantes();
    } catch (error) {
      toast.error('Erro ao deletar ambulante');
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
          <Button className="bg-indigo-600 hover:bg-indigo-700">
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
                        <TableCell>{getStatusBadge(ambulante.status)}</TableCell>
                        <TableCell className="text-right">
                          <div className="flex items-center justify-end space-x-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                              title="Editar"
                            >
                              <Edit size={16} />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-red-600 hover:text-red-700 hover:bg-red-50"
                              onClick={() => handleDelete(ambulante.id)}
                              title="Deletar"
                            >
                              <Trash2 size={16} />
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
    </MainLayout>
  );
};

export default AmbulantesPag;
