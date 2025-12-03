// Serviço de API para comunicação com o backend

import { 
  User, 
  cliente, 
  Categoria, 
  Produto, 
  RegraCobranca, 
  Pedido, 
  Log,
  ApiResponse,
  PaginatedResponse,
  DashboardMetrics,
  RelatorioVendas,
  CalculoCobranca,
  LoginForm,
  clienteForm,
  ProdutoForm,
  CategoriaForm,
  RegraCobrancaForm,
  UserForm,
  PedidoSaidaForm,
  PedidoRetornoForm,
  PedidoRetornoFormComDivida
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

class ApiService {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    };
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Erro desconhecido' }));
      throw new Error(errorData.message || `Erro ${response.status}`);
    }
    return response.json();
  }

  // Autenticação
  async login(credentials: LoginForm): Promise<{ access_token: string; refresh_token: string; user: User }> {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    });
    return this.handleResponse(response);
  }

  async refreshToken(): Promise<{ access_token: string; user: User }> {
    const refreshToken = localStorage.getItem('refresh_token');
    const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        Authorization: `Bearer ${refreshToken}`
      }
    });
    return this.handleResponse(response);
  }

  async getProfile(): Promise<{ user: User }> {
    const response = await fetch(`${API_BASE_URL}/api/auth/profile`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async changePassword(data: { current_password: string; new_password: string; confirm_password: string }): Promise<ApiResponse<void>> {
    const response = await fetch(`${API_BASE_URL}/api/auth/change-password`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return this.handleResponse(response);
  }

  async logout(): Promise<ApiResponse<void>> {
    const response = await fetch(`${API_BASE_URL}/api/auth/logout`, {
      method: 'POST',
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  // clientes
  async getclientes(params?: { page?: number; per_page?: number; search?: string; status?: string }): Promise<PaginatedResponse<cliente>> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) searchParams.append(key, value.toString());
      });
    }
    
    const response = await fetch(`${API_BASE_URL}/api/clientes?${searchParams}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getcliente(id: number): Promise<cliente> {
    const response = await fetch(`${API_BASE_URL}/api/clientes/${id}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async createcliente(data: clienteForm): Promise<{ message: string; cliente: cliente }> {
    const response = await fetch(`${API_BASE_URL}/api/clientes`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return this.handleResponse(response);
  }

  async updatecliente(id: number, data: Partial<clienteForm>): Promise<{ message: string; cliente: cliente }> {
    const response = await fetch(`${API_BASE_URL}/api/clientes/${id}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return this.handleResponse(response);
  }

  async deletecliente(id: number): Promise<ApiResponse<void>> {
    const response = await fetch(`${API_BASE_URL}/api/clientes/${id}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getclientesAtivos(): Promise<cliente[]> {
    const response = await fetch(`${API_BASE_URL}/api/clientes/ativos`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  // Produtos
  async getProdutos(params?: { page?: number; per_page?: number; search?: string; categoria_id?: number; estoque_baixo?: boolean }): Promise<PaginatedResponse<Produto>> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) searchParams.append(key, value.toString());
      });
    }
    
    const response = await fetch(`${API_BASE_URL}/api/produtos?${searchParams}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getProduto(id: number): Promise<Produto> {
    const response = await fetch(`${API_BASE_URL}/api/produtos/${id}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async createProduto(data: ProdutoForm): Promise<{ message: string; produto: Produto }> {
    const response = await fetch(`${API_BASE_URL}/api/produtos`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return this.handleResponse(response);
  }

  async updateProduto(id: number, data: Partial<ProdutoForm>): Promise<{ message: string; produto: Produto }> {
    const response = await fetch(`${API_BASE_URL}/api/produtos/${id}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return this.handleResponse(response);
  }

  async deleteProduto(id: number): Promise<ApiResponse<void>> {
    const response = await fetch(`${API_BASE_URL}/api/produtos/${id}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getProdutosEstoqueBaixo(): Promise<Produto[]> {
    const response = await fetch(`${API_BASE_URL}/api/produtos/estoque-baixo`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async ajustarEstoque(id: number, novoEstoque: number): Promise<{ message: string; produto: Produto; estoque_anterior: number; novo_estoque: number }> {
    const response = await fetch(`${API_BASE_URL}/api/produtos/${id}/ajustar-estoque`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ novo_estoque: novoEstoque })
    });
    return this.handleResponse(response);
  }

  // Categorias
  async getCategorias(params?: { page?: number; per_page?: number; search?: string }): Promise<PaginatedResponse<Categoria>> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) searchParams.append(key, value.toString());
      });
    }
    
    const response = await fetch(`${API_BASE_URL}/api/categorias?${searchParams}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getCategoria(id: number): Promise<Categoria> {
    const response = await fetch(`${API_BASE_URL}/api/categorias/${id}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async createCategoria(data: CategoriaForm): Promise<{ message: string; categoria: Categoria }> {
    const response = await fetch(`${API_BASE_URL}/api/categorias`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return this.handleResponse(response);
  }

  async updateCategoria(id: number, data: Partial<CategoriaForm>): Promise<{ message: string; categoria: Categoria }> {
    const response = await fetch(`${API_BASE_URL}/api/categorias/${id}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return this.handleResponse(response);
  }

  async deleteCategoria(id: number): Promise<ApiResponse<void>> {
    const response = await fetch(`${API_BASE_URL}/api/categorias/${id}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getCategoriasAtivas(): Promise<Categoria[]> {
    const response = await fetch(`${API_BASE_URL}/api/categorias/ativas`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  // Regras de Cobrança
  async getRegrasCobranca(params?: { page?: number; per_page?: number }): Promise<PaginatedResponse<RegraCobranca>> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) searchParams.append(key, value.toString());
      });
    }
    
    const response = await fetch(`${API_BASE_URL}/api/regras-cobranca?${searchParams}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getRegraCobranca(id: number): Promise<RegraCobranca> {
    const response = await fetch(`${API_BASE_URL}/api/regras-cobranca/${id}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async createRegraCobranca(data: RegraCobrancaForm): Promise<{ message: string; regra: RegraCobranca }> {
    const response = await fetch(`${API_BASE_URL}/api/regras-cobranca`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return this.handleResponse(response);
  }

  async updateRegraCobranca(id: number, data: Partial<RegraCobrancaForm>): Promise<{ message: string; regra: RegraCobranca }> {
    const response = await fetch(`${API_BASE_URL}/api/regras-cobranca/${id}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return this.handleResponse(response);
  }

  async deleteRegraCobranca(id: number): Promise<ApiResponse<void>> {
    const response = await fetch(`${API_BASE_URL}/api/regras-cobranca/${id}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async calcularDesconto(valorPago: number): Promise<{ valor_pago: number; calculo: CalculoCobranca }> {
    const response = await fetch(`${API_BASE_URL}/api/regras-cobranca/calcular`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ valor_pago: valorPago })
    });
    return this.handleResponse(response);
  }

  // Usuários
  async getUsuarios(params?: { page?: number; per_page?: number; search?: string; role?: string; active_only?: boolean }): Promise<PaginatedResponse<User>> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) searchParams.append(key, value.toString());
      });
    }
    
    const response = await fetch(`${API_BASE_URL}/api/usuarios?${searchParams}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getUsuario(id: number): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/api/usuarios/${id}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async createUsuario(data: UserForm): Promise<{ message: string; user: User }> {
    const response = await fetch(`${API_BASE_URL}/api/usuarios`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return this.handleResponse(response);
  }

  async updateUsuario(id: number, data: Partial<UserForm>): Promise<{ message: string; user: User }> {
    const response = await fetch(`${API_BASE_URL}/api/usuarios/${id}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return this.handleResponse(response);
  }

  async deleteUsuario(id: number): Promise<ApiResponse<void>> {
    const response = await fetch(`${API_BASE_URL}/api/usuarios/${id}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async resetPassword(id: number, newPassword: string): Promise<ApiResponse<void>> {
    const response = await fetch(`${API_BASE_URL}/api/usuarios/${id}/reset-password`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ new_password: newPassword })
    });
    return this.handleResponse(response);
  }

  // Pedidos
  async getPedidos(params?: { page?: number; per_page?: number; status?: string; cliente_id?: number; data_inicio?: string; data_fim?: string }): Promise<PaginatedResponse<Pedido>> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) searchParams.append(key, value.toString());
      });
    }
    
    const response = await fetch(`${API_BASE_URL}/api/pedidos?${searchParams}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getPedido(id: number): Promise<Pedido> {
    const response = await fetch(`${API_BASE_URL}/api/pedidos/${id}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async createPedidoSaida(data: PedidoSaidaForm): Promise<{ message: string; pedido: Pedido }> {
    const response = await fetch(`${API_BASE_URL}/api/pedidos/saida`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return this.handleResponse(response);
  }

  async updatePedidoSaida(id: number, data: PedidoSaidaForm): Promise<{ message: string; pedido: Pedido }> {
    const response = await fetch(`${API_BASE_URL}/api/pedidos/${id}/saida`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return this.handleResponse(response);
  }

  async registrarRetorno(id: number, data: PedidoRetornoFormComDivida): Promise<{ message: string; pedido: Pedido }> {
    const response = await fetch(`${API_BASE_URL}/api/pedidos/${id}/retorno`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return this.handleResponse(response);
  }

  async imprimirRetorno(id: number): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/api/pedidos/${id}/imprimir_retorno`, {
      headers: {
        ...this.getAuthHeaders(),
        'Accept': 'application/pdf'
      }
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Erro desconhecido ao gerar PDF' }));
      throw new Error(errorData.message || `Erro ${response.status}`);
    }
    return response.blob();
  }

  async finalizarPedido(id: number): Promise<{ message: string; pedido: Pedido }> {
    const response = await fetch(`${API_BASE_URL}/api/pedidos/${id}/finalizar`, {
      method: 'POST',
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async deletePedido(id: number): Promise<ApiResponse<void>> {
    const response = await fetch(`${API_BASE_URL}/api/pedidos/${id}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async imprimirPedido(id: number): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/api/pedidos/${id}/imprimir`, {
      headers: {
        ...this.getAuthHeaders(),
        'Accept': 'application/pdf'
      }
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Erro desconhecido ao gerar PDF' }));
      throw new Error(errorData.message || `Erro ${response.status}`);
    }
    return response.blob();
  }

  // Relatórios
  async getDashboardMetrics(): Promise<DashboardMetrics> {
    const response = await fetch(`${API_BASE_URL}/api/relatorios/dashboard`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  async getRelatorioVendas(params?: { data_inicio?: string; data_fim?: string; cliente_id?: number; produto_id?: number; formato?: 'json' | 'csv' }): Promise<RelatorioVendas | Blob> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) searchParams.append(key, value.toString());
      });
    }
    
    const response = await fetch(`${API_BASE_URL}/api/relatorios/vendas?${searchParams}`, {
      headers: this.getAuthHeaders()
    });
    
    if (params?.formato === 'csv') {
      return response.blob();
    }
    
    return this.handleResponse(response);
  }

  // Logs
  async getLogs(params?: { page?: number; per_page?: number; user_id?: number; action?: string; data_inicio?: string; data_fim?: string }): Promise<PaginatedResponse<Log>> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) searchParams.append(key, value.toString());
      });
    }
    
    const response = await fetch(`${API_BASE_URL}/api/logs?${searchParams}`, {
      headers: this.getAuthHeaders()
    });
    return this.handleResponse(response);
  }

  // Impressão de Notas Fiscais
  async imprimirNotaSaida(pedidoId: number): Promise<Blob> {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE_URL}/api/pedidos/${pedidoId}/imprimir`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error(`Erro ao gerar nota: ${response.status}`);
    }

    const blob = await response.blob();
    return blob;
  }

  async imprimirNotaRetorno(pedidoId: number): Promise<Blob> {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE_URL}/api/pedidos/${pedidoId}/imprimir_retorno`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error(`Erro ao gerar nota: ${response.status}`);
    }

    const blob = await response.blob();
    return blob;
  }
}

export const apiService = new ApiService();
export const api = apiService; // Alias para compatibilidade
