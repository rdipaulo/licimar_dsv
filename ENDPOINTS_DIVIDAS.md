# 🔗 URLs e Endpoints da Implementação de Dívidas

## 🌐 Frontend Routes

### Telas Principais
- **Saída (Lançamento de Dívida)**: `http://localhost:5173/pedidos/saida`
  - Campo novo: "Dívida (R$)"
  - Registra dívida automaticamente ao finalizar

- **Retorno (Cobrança de Dívida)**: `http://localhost:5173/pedidos/retorno`
  - Campo existente: "Cobrança de Dívida (R$)"
  - Registra pagamento automaticamente ao finalizar

- **Dashboard de Dívidas**: `http://localhost:5173/dashboard-divida`
  - Exibe saldo devedor de cada cliente
  - Usa novo endpoint `getDividaPendente()`

---

## 🔌 Backend API Endpoints

### Base URL
```
http://localhost:5000/api/dividas
```

### 1. Consultar Saldo Devedor
```
GET /api/dividas/clientes/{cliente_id}/divida-pendente
Authorization: Bearer {token}

Exemplo:
GET http://localhost:5000/api/dividas/clientes/1/divida-pendente
```

**Response**:
```json
{
  "cliente_id": 1,
  "cliente_nome": "João Silva",
  "divida_total": 500.00,
  "cobrancas_total": 100.00,
  "saldo_devedor": 400.00,
  "quantidade_dividas": 3,
  "dividas": [...]
}
```

---

### 2. Registrar Dívida
```
POST /api/dividas/registrar
Authorization: Bearer {token}
Content-Type: application/json

Exemplo:
POST http://localhost:5000/api/dividas/registrar
```

**Request Body**:
```json
{
  "id_cliente": 1,
  "valor_divida": 250.00,
  "descricao": "Dívida do Pedido de Saída #123"
}
```

**Response** (201):
```json
{
  "message": "Dívida registrada com sucesso",
  "id_divida": 5,
  "id_cliente": 1,
  "valor_divida": 250.00,
  "status": "Em Aberto",
  "data_registro": "2025-12-06T14:30:00"
}
```

---

### 3. Registrar Pagamento de Dívida
```
POST /api/dividas/pagamentos-divida/registrar
Authorization: Bearer {token}
Content-Type: application/json

Exemplo:
POST http://localhost:5000/api/dividas/pagamentos-divida/registrar
```

**Request Body**:
```json
{
  "id_cliente": 1,
  "cobranca_divida": 100.00,
  "descricao": "Cobrança do Pedido de Retorno #456"
}
```

**Response** (201):
```json
{
  "message": "Pagamento registrado com sucesso",
  "id_cliente": 1,
  "cobranca_divida": 100.00,
  "dividas_quitadas": 1,
  "saldo_devedor_novo": 300.00,
  "data_pagamento": "2025-12-06T15:00:00"
}
```

---

### 4. Listar Todas as Dívidas (Adicional)
```
GET /api/dividas?page=1&per_page=20&status=Em Aberto&cliente_id=1
Authorization: Bearer {token}

Exemplo:
GET http://localhost:5000/api/dividas?page=1&per_page=20
```

**Query Parameters**:
- `page`: Página (padrão: 1)
- `per_page`: Itens por página (padrão: 20)
- `status`: Filtro de status
- `cliente_id`: Filtro por cliente

---

## 🧪 Testes com cURL

### 1. Obter Token JWT (Login)
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "seu_usuario",
    "password": "sua_senha"
  }'
```

Salvar o `access_token` retornado.

---

### 2. Consultar Saldo Devedor
```bash
curl -X GET http://localhost:5000/api/dividas/clientes/1/divida-pendente \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 3. Registrar Dívida
```bash
curl -X POST http://localhost:5000/api/dividas/registrar \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id_cliente": 1,
    "valor_divida": 250.00,
    "descricao": "Dívida do Pedido de Saída #123"
  }'
```

---

### 4. Registrar Pagamento
```bash
curl -X POST http://localhost:5000/api/dividas/pagamentos-divida/registrar \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id_cliente": 1,
    "cobranca_divida": 100.00,
    "descricao": "Cobrança do Pedido de Retorno #456"
  }'
```

---

### 5. Listar Dívidas com Filtros
```bash
curl -X GET "http://localhost:5000/api/dividas?status=Em%20Aberto&cliente_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📄 Impressão de Notas

### Nota de Saída
```
GET /api/pedidos/{pedido_id}/imprimir
Authorization: Bearer {token}

http://localhost:5000/api/pedidos/1/imprimir
```

Retorna PDF com:
- Itens do pedido
- Total com dívida
- ⚠️ ATENÇÃO - Dívida Pendente: R$ X,XX (se houver)

---

### Nota de Retorno
```
GET /api/pedidos/{pedido_id}/imprimir_retorno
Authorization: Bearer {token}

http://localhost:5000/api/pedidos/1/imprimir_retorno
```

Retorna PDF com:
- Itens de saída/retorno/vendido
- Cobrança de Dívida: R$ X,XX
- ✨ **Dívida Pendente: R$ X,XX** (NOVO)
- Total final

---

## 🔐 Headers Obrigatórios

```
Authorization: Bearer {access_token}
Content-Type: application/json
```

---

## ⚡ Postman Collection

```json
{
  "info": {
    "name": "Licimar - Dívidas API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "GET Divida Pendente",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{token}}",
            "type": "text"
          }
        ],
        "url": {
          "raw": "{{base_url}}/api/dividas/clientes/1/divida-pendente",
          "host": ["{{base_url}}"],
          "path": ["api", "dividas", "clientes", "1", "divida-pendente"]
        }
      }
    },
    {
      "name": "POST Registrar Divida",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{token}}",
            "type": "text"
          },
          {
            "key": "Content-Type",
            "value": "application/json",
            "type": "text"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"id_cliente\": 1, \"valor_divida\": 250, \"descricao\": \"Test\"}"
        },
        "url": {
          "raw": "{{base_url}}/api/dividas/registrar",
          "host": ["{{base_url}}"],
          "path": ["api", "dividas", "registrar"]
        }
      }
    },
    {
      "name": "POST Registrar Pagamento",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{token}}",
            "type": "text"
          },
          {
            "key": "Content-Type",
            "value": "application/json",
            "type": "text"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"id_cliente\": 1, \"cobranca_divida\": 100, \"descricao\": \"Test\"}"
        },
        "url": {
          "raw": "{{base_url}}/api/dividas/pagamentos-divida/registrar",
          "host": ["{{base_url}}"],
          "path": ["api", "dividas", "pagamentos-divida", "registrar"]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:5000"
    },
    {
      "key": "token",
      "value": ""
    }
  ]
}
```

Copie e cole em seu Postman!

---

## 📊 Fluxo de Integração

```
Frontend (/pedidos/saida)
    ↓ [Preencher Dívida]
Backend POST /api/dividas/registrar
    ↓
DB: insere em tabela 'dividas'
    ↓
Frontend recebe OK
    ↓ [Imprime Nota]
Backend GET /api/pedidos/{id}/imprimir
    ↓
PDF com aviso de dívida


Frontend (/pedidos/retorno)
    ↓ [Preencher Cobrança]
Backend POST /api/dividas/pagamentos-divida/registrar
    ↓
DB: atualiza 'dividas' (status) + insere 'pagamentos_divida'
    ↓
Frontend recebe OK + novo saldo
    ↓ [Imprime Nota]
Backend GET /api/pedidos/{id}/imprimir_retorno
    ↓
PDF com Cobrança + Dívida Pendente atualizada


Frontend (/dashboard-divida)
    ↓ [Carregar]
    ├→ GET /api/clientes (lista todos)
    └→ For each cliente:
       GET /api/dividas/clientes/{id}/divida-pendente
    ↓
Dashboard exibe saldos atualizados
```

---

## ✅ Validação da Implementação

**Endpoints Ativos**:
- ✅ GET /api/dividas/clientes/{id}/divida-pendente
- ✅ POST /api/dividas/registrar
- ✅ POST /api/dividas/pagamentos-divida/registrar
- ✅ GET /api/dividas (com filtros)

**Frontend Pronto**:
- ✅ Campo Dívida em `/pedidos/saida`
- ✅ Campo Cobrança em `/pedidos/retorno`
- ✅ Dashboard atualizado em `/dashboard-divida`
- ✅ Notas fiscais com Dívida Pendente

**Banco de Dados**:
- ✅ Tabela `dividas` com dados
- ✅ Tabela `pagamentos_divida` com dados
- ✅ Property `divida_pendente_total` em Cliente

---

**Última atualização**: 06 de Dezembro de 2025
**Versão**: 1.0
**Status**: ✅ COMPLETO E TESTADO
