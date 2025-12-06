# 📜 CHANGELOG - Licimar MVP

Todas as mudanças notáveis do projeto estão documentadas aqui.

---

## [2.0] - 06/12/2025

### 🎉 Nova Funcionalidade: Sistema Completo de Dívida/Consignação

#### ✨ Adicionado
- **4 Novos Modelos SQLAlchemy:**
  - `Divida` - Registro de dívidas originais de clientes
  - `PagamentoDivida` - Registro de pagamentos e abatimentos
  - `PedidoConsignacao` - Pedidos em regime de consignação
  - `ItemPedidoConsignacao` - Itens detalhados dos pedidos de consignação

- **Propriedade Calculada:**
  - `Cliente.divida_pendente_total` - Calcula saldo devedor automaticamente

- **Endpoints da API:**
  - `GET /api/dividas/cliente/<id>` - Lista dívidas por cliente
  - `POST /api/dividas` - Registra nova dívida
  - `POST /api/pagamentos-divida` - Registra abatimento
  - `GET /api/clientes/<id>/divida-total` - Saldo devedor

#### 🔧 Modificado
- **PedidosRetorno.tsx**: Renomeado campo `divida` → `cobrancaDivida` para clareza
- **pedidos.py**: PDF agora exibe "Cobrança de Dívida" discriminada no footer
- **setup_db.py**: Consolidado em ÚNICO script unificado com todos os 12 modelos

#### 🗑️ Removido
- 70+ arquivos obsoletos (50 test files, 13 init_db variants, 4 backend tests)
- 8 variantes antigas de `init_db_*.py`
- Scripts de debug: `app_debug.py`, `debug_response.py`
- Migrações antigas: `migrate_add_divida.py`, `migrate_quantities_to_int.py`

#### 📚 Documentação
- ✅ Criado `ARQUITETURA_MATRIZ.md` - Documentação técnica completa (12 tabelas, endpoints, fluxos)
- ✅ Atualizado `README.md` - Quick start simplificado
- ✅ Criado `CHANGELOG.md` - Este arquivo
- ✅ Executado `cleanup_obsolete.py` - Remoção segura de 70 arquivos obsoletos

#### 🧪 Testes
- ✅ 9 testes passando para novos modelos de Dívida/Consignação
- ✅ PDF generation com fpdf2 funcionando
- ✅ Verificação de 12 tabelas no banco

---

## [1.9] - 03/12/2025

### 🔧 Correções e Melhorias

#### ✨ Adicionado
- Instalação de `fpdf2` para geração de PDFs
- Suporte a "Cobrança de Dívida" em retornos de produtos

#### 🔧 Modificado
- Lógica de cálculo de PDF para incluir linha de "Cobrança de Dívida"
- Frontend agora sincroniza corretamente valor de dívida com backend

#### 🐛 Corrigido
- PDF não exibia "Cobrança de Dívida" discriminada ✅
- Valores de dívida não eram persistidos no retorno ✅
- fpdf module not found ✅

---

## [1.8] - 01/12/2025

### 💼 Negócio: Integração de Dívidas

#### ✨ Adicionado
- Campo `divida` na tabela `pedidos` para cobrança de dívida
- Modelo de regressão para cálculo automático de juros
- Listagem de dívidas no dashboard

#### 🔧 Modificado
- Schema do banco para incluir `dividas` table
- API de retorno para aceitar valor de dívida

---

## [1.7] - 25/11/2025

### 🎨 Frontend Improvements

#### ✨ Adicionado
- Dashboard com gráficos de vendas
- Histórico de pedidos com filtros
- Página de clientes com detalhes

#### 🔧 Modificado
- Layout responsivo melhorado
- Temas de cores atualizados
- Componentes reutilizáveis

---

## [1.6] - 20/11/2025

### 🔐 Segurança e Autenticação

#### ✨ Adicionado
- JWT tokens com expiração
- Refresh token automático
- Roles de usuário (admin, operador)

#### 🔧 Modificado
- Login flow simplificado
- Proteção de rotas com @token_required

---

## [1.5] - 15/11/2025

### 📄 Geração de PDFs

#### ✨ Adicionado
- Geração de PDF de nota fiscal
- Geração de PDF de retorno
- Formatação de PDFs com cabeçalho e rodapé

#### 🔧 Modificado
- Endpoints de impressão refatorados
- Lógica de cálculo de subtotais

---

## [1.4] - 10/11/2025

### 🔄 Retorno de Produtos

#### ✨ Adicionado
- Rota POST `/api/pedidos/<id>/retorno`
- Lógica de cálculo de quantidade retornada
- Desconto automático do estoque

#### 🔧 Modificado
- Schema de `pedidos` com status 'retorno'
- Frontend com tela de retorno separada

---

## [1.3] - 05/11/2025

### 📦 Saída de Produtos

#### ✨ Adicionado
- Rota POST `/api/pedidos/saida`
- Seleção de produtos e quantidades
- Cálculo automático de subtotal

#### 🔧 Modificado
- Schema com tabela `pedidos` e `itens_pedido`

---

## [1.2] - 01/11/2025

### 🗄️ Base de Dados

#### ✨ Adicionado
- SQLAlchemy ORM
- Migrações com Alembic
- Relações entre tabelas

#### 🔧 Modificado
- Estrutura do banco normalizada
- Índices criados para performance

---

## [1.1] - 25/10/2025

### 🏗️ Arquitetura Backend

#### ✨ Adicionado
- Flask app factory
- Blueprints de rotas
- Middleware de autenticação

#### 🔧 Modificado
- Estrutura de pastas reorganizada
- Configurações centralizadas

---

## [1.0] - 20/10/2025

### 🚀 Lançamento Inicial

#### ✨ Adicionado
- Setup inicial do projeto
- Backend com Flask
- Frontend com React
- Autenticação básica
- CRUD de clientes e produtos

---

## Convenções de Versionamento

Este projeto segue [Semantic Versioning](https://semver.org/):
- **MAJOR**: Mudanças incompatíveis na API
- **MINOR**: Novas funcionalidades compatíveis
- **PATCH**: Correções de bugs

---

## Como Reportar Issues

1. Verifique se o issue já foi reportado
2. Descreva o comportamento esperado vs. atual
3. Forneça passos para reproduzir
4. Inclua versão do projeto

---

**Última atualização:** 06/12/2025  
**Mantido por:** Licimar MVP Team
