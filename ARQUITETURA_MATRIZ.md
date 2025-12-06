# 📐 ARQUITETURA & DOCUMENTAÇÃO MATRIZ - LICIMAR MVP

**Versão:** 2.0  
**Data:** 06/12/2025  
**Status:** ✅ Produção

---

## 📑 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Stack Tecnológico](#stack-tecnológico)
4. [Estrutura de Pastas](#estrutura-de-pastas)
5. [Modelos de Dados](#modelos-de-dados)
6. [Endpoints da API](#endpoints-da-api)
7. [Setup e Instalação](#setup-e-instalação)
8. [Fluxos de Negócio](#fluxos-de-negócio)
9. [Configuração](#configuração)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

**Licimar MVP** é um sistema de gerenciamento de vendas e distribuição para vendedores ambulantes, com funcionalidades de:
- Registro de saída de produtos
- Registro de retorno/devolução
- Cálculo automático de subtotais
- Controle de dívidas e consignação
- Geração de PDFs de notas fiscais
- Dashboard com relatórios

### Usuários Principais
- **Vendedor Ambulante**: Registra saídas, retornos, paga dívidas
- **Admin**: Gerencia produtos, clientes, relatórios
- **Operador**: Acessos limitados ao sistema

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React/Vite)                │
│  ┌──────────────────────────────────────────────────┐   │
│  │ • Pedidos (Saída, Retorno)                      │   │
│  │ • Histórico de Pedidos                           │   │
│  │ • Dashboard de Clientes                          │   │
│  │ • Produtos e Categorias                          │   │
│  │ • Relatórios                                     │   │
│  └──────────────────────────────────────────────────┘   │
│                          ↕ (REST API)                    │
│  ┌──────────────────────────────────────────────────┐   │
│  │              BACKEND (Flask + SQLAlchemy)        │   │
│  │  ┌─────────────────────────────────────────┐    │   │
│  │  │ Rotas:                                  │    │   │
│  │  │ • /api/pedidos        (Saída/Retorno)  │    │   │
│  │  │ • /api/clientes       (Clientes)        │    │   │
│  │  │ • /api/produtos       (Produtos)        │    │   │
│  │  │ • /api/categorias     (Categorias)      │    │   │
│  │  │ • /api/auth          (Autenticação)     │    │   │
│  │  │ • /api/relatorios    (Relatórios)      │    │   │
│  │  │ • /api/dividas       (Dívidas)         │    │   │
│  │  │ • /api/consignacao   (Consignação)     │    │   │
│  │  └─────────────────────────────────────────┘    │   │
│  │                                                  │   │
│  │  ┌─────────────────────────────────────────┐    │   │
│  │  │ Modelos SQLAlchemy:                     │    │   │
│  │  │ • User, Cliente, Categoria, Produto     │    │   │
│  │  │ • Pedido, ItemPedido, RegraCobranca    │    │   │
│  │  │ • Divida, PagamentoDivida              │    │   │
│  │  │ • PedidoConsignacao, ItemConsignacao   │    │   │
│  │  │ • Log                                   │    │   │
│  │  └─────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────┘   │
│                          ↕ (SQLite/ORM)                 │
│  ┌──────────────────────────────────────────────────┐   │
│  │           BASE DE DADOS (SQLite)                │   │
│  │  • 12 Tabelas principais                        │   │
│  │  • Relacionamentos many-to-one, one-to-many    │   │
│  │  • Transações ACID                              │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 💾 Stack Tecnológico

### Backend
| Componente | Versão | Propósito |
|-----------|--------|----------|
| Flask | 3.1.0 | Framework Web |
| SQLAlchemy | 2.0.40 | ORM |
| Flask-SQLAlchemy | 3.1.1 | Integração BD |
| Flask-JWT-Extended | 4.6.0 | Autenticação JWT |
| Flask-CORS | 4.0.0 | CORS |
| fpdf2 | 2.8.5 | Geração de PDFs |
| pytz | 2024.1 | Timezone |

### Frontend
| Componente | Versão | Propósito |
|-----------|--------|----------|
| React | 18.x | Framework UI |
| TypeScript | 5.x | Tipagem |
| Vite | 5.x | Build tool |
| Tailwind CSS | 3.x | Styling |
| lucide-react | 1.x | Ícones |

### Banco de Dados
| Componente | Versão |
|-----------|--------|
| SQLite | 3.x |

---

## 📂 Estrutura de Pastas

```
licimar_dsv/
├── backend/
│   └── licimar_mvp_app/
│       ├── src/
│       │   ├── __init__.py
│       │   ├── main.py                    # Configuração da app
│       │   ├── database.py                # Inicialização do BD
│       │   ├── config.py                  # Configurações
│       │   ├── models.py                  # Modelos SQLAlchemy ⭐
│       │   ├── routes/
│       │   │   ├── __init__.py
│       │   │   ├── auth.py               # Autenticação
│       │   │   ├── pedidos.py            # Pedidos (SAÍDA/RETORNO)
│       │   │   ├── clientes.py           # Clientes
│       │   │   ├── produtos.py           # Produtos
│       │   │   ├── categorias.py         # Categorias
│       │   │   ├── regras_cobranca.py    # Regras de Cobrança
│       │   │   ├── usuarios.py           # Usuários
│       │   │   ├── relatorios.py         # Relatórios
│       │   │   └── logs.py               # Logs
│       │   └── utils/
│       │       ├── decorators.py         # Decoradores (@token_required)
│       │       ├── helpers.py            # Funções auxiliares
│       │       └── constants.py          # Constantes
│       ├── instance/
│       │   └── licimar_dev.db            # Banco SQLite ⭐
│       ├── app.py                        # Entry point
│       ├── setup_db.py                   # 🎯 Setup unificado do BD
│       ├── requirements.txt              # Dependências
│       ├── Dockerfile                    # Containerização
│       └── Procfile                      # Deploy Heroku
├── frontend/
│   └── licimar_mvp_frontend/
│       ├── src/
│       │   ├── pages/
│       │   │   ├── Pedidos/
│       │   │   │   ├── PedidosSaida.tsx       # Tela de saída
│       │   │   │   ├── PedidosRetorno.tsx    # Tela de retorno
│       │   │   │   └── Historico.tsx         # Histórico
│       │   │   ├── Clientes.tsx
│       │   │   ├── Produtos.tsx
│       │   │   ├── Dashboard.tsx
│       │   │   └── Login.tsx
│       │   ├── components/
│       │   │   ├── MainLayout.tsx
│       │   │   ├── ui/                  # Componentes reutilizáveis
│       │   │   └── ...
│       │   ├── services/
│       │   │   └── api.ts              # Cliente HTTP/API
│       │   ├── types/
│       │   │   └── index.ts            # Tipos TypeScript
│       │   ├── hooks/
│       │   │   └── use-toast.ts
│       │   └── App.tsx
│       ├── vite.config.ts
│       ├── tsconfig.json
│       ├── package.json
│       ├── tailwind.config.js
│       └── Dockerfile
├── documentacao/
│   └── ...
├── ARQUITETURA_MATRIZ.md               # 📄 Este arquivo
├── setup_db.py                         # Setup unificado
└── requirements.txt                    # Dependências Python
```

---

## 📊 Modelos de Dados

### 12 Tabelas Principais

#### 1. **users**
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username VARCHAR(80) UNIQUE NOT NULL,
  email VARCHAR(120) UNIQUE NOT NULL,
  password_hash VARCHAR(255),
  role VARCHAR(20) DEFAULT 'operador',
  active BOOLEAN DEFAULT TRUE,
  created_at DATETIME,
  updated_at DATETIME
);
```

#### 2. **clientes**
```sql
CREATE TABLE clientes (
  id INTEGER PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  email VARCHAR(120) UNIQUE,
  telefone VARCHAR(20),
  cpf VARCHAR(14) UNIQUE,
  endereco TEXT,
  status VARCHAR(20) DEFAULT 'ativo',
  divida_acumulada NUMERIC(10,2) DEFAULT 0,
  created_at DATETIME,
  updated_at DATETIME
);
-- Propriedade: divida_pendente_total (calculada dinamicamente)
```

#### 3. **categorias**
```sql
CREATE TABLE categorias (
  id INTEGER PRIMARY KEY,
  nome VARCHAR(100) UNIQUE NOT NULL,
  descricao TEXT,
  active BOOLEAN DEFAULT TRUE,
  created_at DATETIME,
  updated_at DATETIME
);
```

#### 4. **produtos**
```sql
CREATE TABLE produtos (
  id INTEGER PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  preco NUMERIC(10,2) NOT NULL,
  estoque INTEGER DEFAULT 0,
  categoria_id INTEGER FK,
  imagem_url VARCHAR(255),
  descricao TEXT,
  active BOOLEAN DEFAULT TRUE,
  estoque_minimo INTEGER DEFAULT 10,
  nao_devolve BOOLEAN DEFAULT FALSE,  -- Gelo seco, etc
  peso NUMERIC(5,2) DEFAULT 0,
  created_at DATETIME,
  updated_at DATETIME
);
```

#### 5. **pedidos**
```sql
CREATE TABLE pedidos (
  id INTEGER PRIMARY KEY,
  cliente_id INTEGER FK NOT NULL,
  data_operacao DATETIME,
  status VARCHAR(20) DEFAULT 'saida',  -- 'saida', 'retorno', 'finalizado'
  total NUMERIC(10,2) DEFAULT 0,
  divida NUMERIC(10,2) DEFAULT 0,      -- Cobrança de dívida
  observacoes TEXT,
  created_at DATETIME,
  updated_at DATETIME
);
```

#### 6. **itens_pedido**
```sql
CREATE TABLE itens_pedido (
  id INTEGER PRIMARY KEY,
  pedido_id INTEGER FK NOT NULL,
  produto_id INTEGER FK NOT NULL,
  quantidade_saida NUMERIC(10,3),
  quantidade_retorno INTEGER DEFAULT 0,
  preco_unitario NUMERIC(10,2),
  created_at DATETIME
);
```

#### 7. **dividas**
```sql
CREATE TABLE dividas (
  id_divida INTEGER PRIMARY KEY,
  id_cliente INTEGER FK NOT NULL,
  data_registro DATETIME,
  valor_divida NUMERIC(10,2),
  descricao VARCHAR(255),
  status VARCHAR(50) DEFAULT 'Em Aberto',
  created_at DATETIME,
  updated_at DATETIME
);
```

#### 8. **pagamentos_divida**
```sql
CREATE TABLE pagamentos_divida (
  id_lancamento INTEGER PRIMARY KEY,
  id_divida INTEGER FK NOT NULL,
  data_pagamento DATETIME,
  cobranca_divida NUMERIC(10,2),
  id_nota_venda INTEGER,
  descricao VARCHAR(255),
  created_at DATETIME
);
```

#### 9. **pedidos_consignacao**
```sql
CREATE TABLE pedidos_consignacao (
  id_pedido INTEGER PRIMARY KEY,
  id_cliente INTEGER FK NOT NULL,
  data_pedido DATETIME,
  tipo_operacao VARCHAR(50),
  valor_total_final NUMERIC(10,2) DEFAULT 0,
  status VARCHAR(50) DEFAULT 'Aberto',
  observacoes TEXT,
  created_at DATETIME,
  updated_at DATETIME
);
```

#### 10. **itens_pedido_consignacao**
```sql
CREATE TABLE itens_pedido_consignacao (
  id_item_pedido INTEGER PRIMARY KEY,
  id_pedido INTEGER FK NOT NULL,
  id_produto INTEGER FK NOT NULL,
  quantidade_negociada NUMERIC(10,2),
  valor_unitario_venda NUMERIC(10,2),
  subtotal NUMERIC(10,2),
  created_at DATETIME
);
```

#### 11. **regras_cobranca**
```sql
CREATE TABLE regras_cobranca (
  id INTEGER PRIMARY KEY,
  faixa_inicial NUMERIC(10,2),
  faixa_final NUMERIC(10,2),
  percentual NUMERIC(5,2),
  descricao VARCHAR(255),
  active BOOLEAN DEFAULT TRUE,
  created_at DATETIME,
  updated_at DATETIME
);
```

#### 12. **logs**
```sql
CREATE TABLE logs (
  id INTEGER PRIMARY KEY,
  user_id INTEGER FK,
  action VARCHAR(100) NOT NULL,
  details TEXT,
  ip_address VARCHAR(45),
  user_agent TEXT,
  created_at DATETIME
);
```

---

## 🔌 Endpoints da API

### Autenticação
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/auth/login` | Login e retorna JWT |
| POST | `/api/auth/refresh` | Refresh token |
| POST | `/api/auth/logout` | Logout |

### Pedidos
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/pedidos` | Lista pedidos (paginado) |
| GET | `/api/pedidos/<id>` | Obtém pedido específico |
| POST | `/api/pedidos/saida` | Cria pedido de saída |
| PUT | `/api/pedidos/<id>/saida` | Atualiza saída |
| POST | `/api/pedidos/<id>/retorno` | Registra retorno |
| GET | `/api/pedidos/<id>/itens` | Lista itens do pedido |
| GET | `/api/pedidos/<id>/imprimir` | Gera PDF de saída |
| GET | `/api/pedidos/<id>/imprimir_retorno` | Gera PDF de retorno |
| DELETE | `/api/pedidos/<id>` | Deleta pedido (admin) |

### Clientes
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/clientes` | Lista clientes (paginado) |
| GET | `/api/clientes/ativos` | Lista clientes ativos |
| GET | `/api/clientes/<id>` | Obtém cliente |
| POST | `/api/clientes` | Cria cliente |
| PUT | `/api/clientes/<id>` | Atualiza cliente |
| DELETE | `/api/clientes/<id>` | Deleta cliente (admin) |

### Produtos
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/produtos` | Lista produtos (paginado) |
| GET | `/api/produtos/<id>` | Obtém produto |
| POST | `/api/produtos` | Cria produto (admin) |
| PUT | `/api/produtos/<id>` | Atualiza produto (admin) |
| DELETE | `/api/produtos/<id>` | Deleta produto (admin) |

### Categorias
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/categorias` | Lista categorias |
| POST | `/api/categorias` | Cria categoria (admin) |
| PUT | `/api/categorias/<id>` | Atualiza categoria (admin) |
| DELETE | `/api/categorias/<id>` | Deleta categoria (admin) |

### Dívidas
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/dividas/cliente/<cliente_id>` | Lista dívidas do cliente |
| POST | `/api/dividas` | Cria dívida (admin) |
| POST | `/api/pagamentos-divida` | Registra abatimento |
| GET | `/api/clientes/<id>/divida-total` | Saldo devedor total |

### Consignação
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/pedidos-consignacao` | Cria pedido consignação |
| GET | `/api/pedidos-consignacao` | Lista pedidos consignação |
| PUT | `/api/pedidos-consignacao/<id>` | Atualiza pedido |
| DELETE | `/api/pedidos-consignacao/<id>` | Deleta pedido |

### Relatórios
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/relatorios/vendas` | Relatório de vendas |
| GET | `/api/relatorios/clientes` | Relatório de clientes |
| GET | `/api/relatorios/dividas` | Relatório de dívidas |

---

## 🚀 Setup e Instalação

### Pré-requisitos
- Python 3.10+
- Node.js 18+
- npm ou yarn
- Git

### Backend Setup

```bash
# 1. Clonar repositório
git clone <repo-url>
cd licimar_dsv

# 2. Criar venv e ativar
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 3. Instalar dependências
pip install -r backend/licimar_mvp_app/requirements.txt

# 4. Instalar fpdf2
pip install fpdf2

# 5. Setup unificado do banco de dados
cd backend/licimar_mvp_app
python setup_db.py

# 6. Iniciar servidor
python app.py
```

### Frontend Setup

```bash
# 1. Navegar para frontend
cd frontend/licimar_mvp_frontend

# 2. Instalar dependências
npm install

# 3. Iniciar dev server
npm run dev

# 4. Acessar
http://localhost:5173
```

---

## 💼 Fluxos de Negócio

### 1. Saída de Produtos
```
Cliente → Sistema → Registra Saída
                  ├─ Seleciona produtos
                  ├─ Define quantidades
                  ├─ Sistema calcula total
                  └─ Gera PDF de nota fiscal
```

### 2. Retorno de Produtos
```
Cliente → Sistema → Retorno
                  ├─ Seleciona pedido
                  ├─ Informa quantidades retornadas
                  ├─ Cobra "Cobrança de Dívida" (opcional)
                  ├─ Sistema calcula novo total
                  ├─ Finaliza pedido
                  └─ Gera PDF de retorno
```

### 3. Controle de Dívidas
```
Dívida Original → Sistema → Registra
                         ├─ Valor inicial
                         ├─ Data
                         └─ Status: 'Em Aberto'
                         
Abatimento → Sistema → Registra Pagamento
                     ├─ Dívida referente
                     ├─ Valor cobrado
                     └─ Data do abatimento
                     
Total Devedor = Σ(valor_divida) - Σ(cobranca_divida)
```

### 4. Consignação
```
Novo Pedido → Sistema → Registra
                      ├─ Tipo: RETIRADA/DEVOLUÇÃO/ACERTO
                      ├─ Itens e quantidades
                      └─ Calcula total
```

---

## ⚙️ Configuração

### Variáveis de Ambiente

**`.env` (Backend)**
```env
FLASK_ENV=development
DATABASE_URL=sqlite:///instance/licimar_dev.db
JWT_SECRET_KEY=seu-secret-key-super-seguro
CORS_ORIGINS=*
```

**`.env` (Frontend)**
```env
VITE_API_BASE_URL=http://localhost:5000
```

---

## 🔍 Troubleshooting

### Erro: "No module named 'fpdf'"
```bash
pip install fpdf2
```

### Erro: "Database locked"
- Feche todas as conexões
- Delete `instance/licimar_dev.db`
- Execute `python setup_db.py`

### JWT Token expirado
- Faça login novamente
- Token de refresh automático após 24h

### CORS Error
- Verifique `CORS_ORIGINS` no `.env`
- Certifique-se que frontend e backend estão na mesma origem

---

## 📝 Convenções

### Nomenclatura
- **Tabelas**: lowercase_com_underscore
- **Colunas**: lowercase_com_underscore
- **FKs**: id_tabela
- **Classes Python**: PascalCase
- **Funções**: snake_case
- **Rotas**: /api/recurso (plural)

### Status de Pedidos
- `saida`: Produto saiu, cliente tem
- `retorno`: Cliente devolveu
- `finalizado`: Pedido encerrado

### Status de Dívidas
- `Em Aberto`: Sem pagamentos
- `Parcialmente Pago`: Alguns abatimentos
- `Quitado`: Saldo zero

---

## 🔐 Segurança

- ✅ JWT para autenticação
- ✅ Hashe de senhas com Werkzeug
- ✅ CORS habilitado
- ✅ Logs de auditoria
- ✅ Validação de entrada

---

## 📋 Checklist de Deployment

- [ ] Variáveis de ambiente configuradas
- [ ] Banco de dados inicializado
- [ ] JWT_SECRET_KEY alterada
- [ ] CORS_ORIGINS configurado
- [ ] Frontend build otimizado (`npm run build`)
- [ ] Backend em modo produção
- [ ] SSL/HTTPS ativado
- [ ] Backups do banco configurados

---

**Documento mantido pelo: Equipe de Desenvolvimento**  
**Última atualização: 06/12/2025**  
**Versão: 2.0**
