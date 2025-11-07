// Tipos para o sistema Licimar

export interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'operador';
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Ambulante {
  id: number;
  nome: string;
  email?: string;
  telefone?: string;
  cpf?: string;
  endereco?: string;
  status: 'ativo' | 'inativo';
  created_at: string;
  updated_at: string;
}

export interface Categoria {
  id: number;
  nome: string;
  descricao?: string;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Produto {
  id: number;
  nome: string;
  preco: number;
  estoque: number;
  categoria_id?: number;
  categoria_nome?: string;
  imagem_url?: string;
  descricao?: string;
  active: boolean;
  estoque_minimo: number;
  estoque_baixo: boolean;
  created_at: string;
  updated_at: string;
}

export interface RegraCobranca {
  id: number;
  faixa_inicial: number;
  faixa_final: number;
  percentual: number;
  descricao?: string;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ItemPedido {
  id: number;
  pedido_id: number;
  produto_id: number;
  produto_nome?: string;
  quantidade_saida: number;
  quantidade_retorno: number;
  quantidade_vendida: number;
  preco_unitario: number;
  valor_total: number;
  created_at: string;
}

export interface Pedido {
  id: number;
  ambulante_id: number;
  ambulante_nome?: string;
  data_operacao: string;
  status: 'saida' | 'retorno' | 'finalizado';
  total: number;
  observacoes?: string;
  itens: ItemPedido[];
  created_at: string;
  updated_at: string;
}

export interface Log {
  id: number;
  user_id?: number;
  username?: string;
  action: string;
  details?: string;
  ip_address?: string;
  user_agent?: string;
  created_at: string;
}

export interface ApiResponse<T> {
  message?: string;
  data?: T;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  pagination: {
    page: number;
    pages: number;
    per_page: number;
    total: number;
    has_next: boolean;
    has_prev: boolean;
    next_num?: number;
    prev_num?: number;
  };
}

export interface DashboardMetrics {
  vendas_periodo: number;
  vendas_hoje: number;
  produtos_estoque_baixo: number;
  ambulantes_ativos: number;
  pedidos_abertos: number;
  produto_mais_vendido: {
    nome?: string;
    quantidade: number;
  };
  vendas_por_dia: Array<{
    data: string;
    vendas: number;
  }>;
}

export interface RelatorioVendas {
  filtros: {
    data_inicio?: string;
    data_fim?: string;
    ambulante_id?: number;
    produto_id?: number;
  };
  resumo: {
    total_vendas: number;
    total_itens: number;
    total_registros: number;
  };
  dados: Array<{
    pedido_id: number;
    data_operacao: string;
    ambulante_nome: string;
    produto_nome: string;
    quantidade_saida: number;
    quantidade_retorno: number;
    quantidade_vendida: number;
    preco_unitario: number;
    valor_total: number;
  }>;
}

export interface CalculoCobranca {
  regra_id?: number;
  percentual: number;
  desconto: number;
  valor_final: number;
  descricao: string;
}

// Tipos para formulários
export interface LoginForm {
  username: string;
  password: string;
}

export interface AmbulanteForm {
  nome: string;
  email?: string;
  telefone?: string;
  cpf?: string;
  endereco?: string;
  status: 'ativo' | 'inativo';
}

export interface ProdutoForm {
  nome: string;
  preco: number;
  estoque: number;
  categoria_id?: number;
  imagem_url?: string;
  descricao?: string;
  estoque_minimo: number;
}

export interface CategoriaForm {
  nome: string;
  descricao?: string;
}

export interface RegraCobrancaForm {
  faixa_inicial: number;
  faixa_final: number;
  percentual: number;
  descricao?: string;
}

export interface UserForm {
  username: string;
  email: string;
  password?: string;
  role: 'admin' | 'operador';
}

export interface PedidoSaidaForm {
  ambulante_id: number;
  itens_saida: Array<{
    produto_id: number;
    quantidade_saida: number;
  }>;
  observacoes?: string;
}

export interface PedidoRetornoForm {
  itens: Array<{
    produto_id: number;
    quantidade_retorno: number;
  }>;
  observacoes?: string;
}
