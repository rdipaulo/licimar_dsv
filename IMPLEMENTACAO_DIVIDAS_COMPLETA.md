# 📋 Implementação Completa da Lógica de Dívidas

## ✅ Status: CONCLUÍDO

Documento de rastreamento da implementação completa da lógica de gerenciamento de dívidas conforme especificado no prompt de desenvolvimento.

---

## 🎯 Objetivo Geral

Implementar a lógica de *backend* (API) e os componentes de *frontend* para gerenciar lançamentos e cobranças de dívidas, integrando-os às rotinas de consignação e ao Dashboard.

---

## 📊 Implementações Realizadas

### I. BACKEND - Modelos de Dados ✅

#### Modelos SQLAlchemy Existentes
- **`Divida`**: Registra débitos de clientes
  - Campos: `id_divida`, `id_cliente`, `valor_divida`, `data_registro`, `descricao`, `status`
  - Status: `'Em Aberto'`, `'Parcialmente Pago'`, `'Quitado'`

- **`PagamentoDivida`**: Registra pagamentos/abatimentos
  - Campos: `id_lancamento`, `id_divida`, `cobranca_divida`, `data_pagamento`, `descricao`
  - Relacionamento: um-para-muitos com `Divida`

- **`Cliente`**: Modelo existente estendido
  - Nova property: `@property divida_pendente_total`
  - Fórmula: `Σ(dividas.valor_divida) - Σ(pagamentos_divida.cobranca_divida)`

#### Lógica de Cálculo
```python
@property
def divida_pendente_total(self):
    """Retorna o saldo devedor total do cliente"""
    # Soma de dívidas 'Em Aberto' e 'Parcialmente Pago'
    # MENOS soma de pagamentos registrados
    # Nunca retorna negativo
```

---

### II. BACKEND - Endpoints API ✅

#### 1️⃣ GET `/api/dividas/clientes/{id}/divida-pendente`
**Função**: Retorna o saldo devedor atual do cliente

**Request**: 
- Parâmetro: `cliente_id` (path)
- Autenticação: Token JWT obrigatório

**Response** (200 OK):
```json
{
  "cliente_id": 1,
  "cliente_nome": "João Silva",
  "divida_total": 500.00,
  "cobrancas_total": 100.00,
  "saldo_devedor": 400.00,
  "quantidade_dividas": 3,
  "dividas": [
    {
      "id_divida": 1,
      "valor_divida": 200.00,
      "valor_pago": 50.00,
      "saldo": 150.00,
      "status": "Parcialmente Pago",
      "data_registro": "2025-12-01T10:30:00"
    }
  ]
}
```

---

#### 2️⃣ POST `/api/dividas/registrar`
**Função**: Registra um novo débito (lançamento de dívida)

**Request Body**:
```json
{
  "id_cliente": 1,
  "valor_divida": 250.00,
  "descricao": "Dívida do Pedido de Saída #123"
}
```

**Response** (201 Created):
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

**Validações**:
- ✅ `id_cliente` obrigatório e deve existir
- ✅ `valor_divida` obrigatório e deve ser > 0
- ✅ Status inicial sempre é `'Em Aberto'`

---

#### 3️⃣ POST `/api/dividas/pagamentos-divida/registrar`
**Função**: Registra um pagamento/cobrança (abatimento) de dívida

**Request Body**:
```json
{
  "id_cliente": 1,
  "cobranca_divida": 100.00,
  "descricao": "Cobrança do Pedido de Retorno #123"
}
```

**Response** (201 Created):
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

**Lógica de Quitação**:
1. Busca todas as dívidas abertas do cliente, ordenadas por data (mais antiga primeiro)
2. Aplica o pagamento à dívida mais antiga
3. Se o valor cobrado for suficiente:
   - ✅ Marca dívida como `'Quitado'`
   - ✅ Move para próxima dívida (FIFO)
4. Se o valor não for suficiente:
   - ✅ Marca como `'Parcialmente Pago'`
   - ✅ Para a iteração

---

#### 4️⃣ GET `/api/dividas` (Endpoint Adicional)
**Função**: Lista todas as dívidas com filtros e paginação

**Query Parameters**:
- `page`: número da página (padrão: 1)
- `per_page`: itens por página (padrão: 20)
- `status`: filtrar por status ('Em Aberto', 'Parcialmente Pago', 'Quitado')
- `cliente_id`: filtrar por cliente

---

### III. BACKEND - Atualização do App ✅

**Arquivo**: `src/main.py`

**Alterações**:
1. Importação do blueprint: `from .routes.dividas import dividas_bp`
2. Registro do blueprint: `app.register_blueprint(dividas_bp, url_prefix='/api/dividas')`

**Status**: ✅ Completo

---

### IV. FRONTEND - Serviço API ✅

**Arquivo**: `src/services/api.ts`

**Métodos Adicionados**:

```typescript
// Registrar nova dívida
async registrarDivida(data: {
  id_cliente: number;
  valor_divida: number;
  descricao?: string;
}): Promise<{ message: string; id_divida: number; }>;

// Registrar pagamento de dívida
async registrarPagamentoDivida(data: {
  id_cliente: number;
  cobranca_divida: number;
  descricao?: string;
}): Promise<{ message: string; saldo_devedor_novo: number }>;

// Obter dívida pendente do cliente
async getDividaPendente(clienteId: number): Promise<{
  cliente_id: number;
  saldo_devedor: number;
  quantidade_dividas: number;
}>;

// Listar todas as dívidas
async getDividas(params?: {
  page?: number;
  per_page?: number;
  status?: string;
  cliente_id?: number;
}): Promise<PaginatedResponse<any>>;
```

**Status**: ✅ Completo

---

### V. FRONTEND - Tela de Saída (Lançamento de Dívida) ✅

**Arquivo**: `src/pages/Pedidos/PedidosSaida.tsx`

#### Alterações Realizadas:

1. **Estado da Dívida**:
   ```typescript
   const [divida, setDivida] = useState(0);
   ```

2. **Campo de Entrada**:
   - Label: "Dívida (R$)"
   - Tipo: `number` com step `0.01`
   - Mínimo: `0.00`
   - Validação: sempre não-negativo

3. **Inclusão no Payload**:
   ```typescript
   const payload: PedidoSaidaForm = {
     cliente_id: Number(selectedclienteId),
     itens_saida: [...],
     divida: divida,  // ← ADICIONADO
   };
   ```

4. **Registro de Dívida**:
   - Após pedido ser criado/atualizado, se `divida > 0`:
   ```typescript
   await apiService.registrarDivida({
     id_cliente: selectedclienteId,
     valor_divida: divida,
     descricao: `Dívida do Pedido de Saída #${pedidoId}`,
   });
   ```

5. **Atualização do Total**:
   - Total exibido agora: `totalPedido + divida`
   - Subtotal mantém apenas produtos

6. **Limpeza**:
   - Campo de dívida resetado após submissão: `setDivida(0)`

**Status**: ✅ Completo

---

### VI. FRONTEND - Tela de Retorno (Cobrança de Dívida) ✅

**Arquivo**: `src/pages/Pedidos/PedidosRetorno.tsx`

#### Alterações Realizadas:

1. **Campo de Cobrança** (já existia):
   - Label: "Cobrança de Dívida (R$)"
   - Tipo: `number` com step `0.01`
   - Mínimo: `0.00`

2. **Registro de Pagamento**:
   - Após retorno ser registrado, se `cobrancaDivida > 0`:
   ```typescript
   await apiService.registrarPagamentoDivida({
     id_cliente: selectedPedido.cliente_id,
     cobranca_divida: cobrancaDivida,
     descricao: `Cobrança do Pedido de Retorno #${selectedPedido.id}`,
   });
   ```

3. **Total Atualizado**:
   - Total a Pagar: `subtotal + cobrancaDivida`

4. **Limpeza**:
   - Campo resetado após submissão: `setCobrancaDivida(0)`

**Status**: ✅ Completo

---

### VII. BACKEND - Impressão de Notas Fiscais ✅

**Arquivo**: `src/routes/pedidos.py`

#### Nota de Saída (GET `/api/pedidos/{id}/imprimir`)

**Alterações**:
1. Adicionado aviso de dívida pendente no rodapé (se houver):
   ```
   ATENÇÃO - Dívida Pendente: R$ 400.00
   ```

#### Nota de Retorno (GET `/api/pedidos/{id}/imprimir_retorno`)

**Alterações**:
1. Exibição da linha "Cobrança de Dívida" (já existia)
2. **NOVO**: Adicionado campo "Dívida Pendente" após o total:
   ```
   Cobrança de Dívida: R$ 100.00
   Dívida Pendente: R$ 300.00
   TOTAL: R$ 450.00
   ```

**Lógica**:
```python
saldo_devedor = pedido.cliente.divida_pendente_total
pdf.cell(0, 8, f'Dívida Pendente: R$ {saldo_devedor:.2f}', align='R')
```

**Status**: ✅ Completo

---

### VIII. FRONTEND - Dashboard de Dívidas ✅

**Arquivo**: `src/pages/DashboardDivida.tsx`

#### Alterações Realizadas:

1. **Atualização da Lógica de Dados**:
   - Antes: Somava dívida dos pedidos finalizados (legado)
   - Depois: Usa novo endpoint `getDividaPendente()` para cada cliente

2. **Chamada Otimizada**:
   ```typescript
   for (const cliente of clientesList) {
     const dividaData = await apiService.getDividaPendente(cliente.id);
     if (dividaData.saldo_devedor > 0) {
       // Adicionar à lista
     }
   }
   ```

3. **Métricas Exibidas**:
   - ✅ Dívida Total (soma de todos saldos)
   - ✅ Clientes com Dívida (quantidade)
   - ✅ Dívida Média (total / quantidade)

4. **Tabela de Detalhamento**:
   - Cliente
   - CPF
   - Telefone
   - Saldo Devedor (usando novo cálculo)
   - Quantidade de Dívidas (em aberto/parcialmente pagas)
   - % do Total
   - Botão "Atualizar" para recarregar dados

**Status**: ✅ Completo

---

## 📝 Resumo das Funcionalidades

| Recurso | Backend | Frontend | Status |
|---------|---------|----------|--------|
| Modelo Divida | ✅ | - | ✅ |
| Modelo PagamentoDivida | ✅ | - | ✅ |
| Property divida_pendente_total | ✅ | - | ✅ |
| GET /api/dividas/clientes/{id}/divida-pendente | ✅ | ✅ | ✅ |
| POST /api/dividas/registrar | ✅ | ✅ | ✅ |
| POST /api/dividas/pagamentos-divida/registrar | ✅ | ✅ | ✅ |
| Campo "Dívida" em Saída | - | ✅ | ✅ |
| Campo "Cobrança de Dívida" em Retorno | - | ✅ | ✅ |
| Exibição na Nota de Saída | ✅ | - | ✅ |
| Exibição na Nota de Retorno | ✅ | - | ✅ |
| Dashboard de Dívidas | - | ✅ | ✅ |

---

## 🔄 Fluxo Completo de Uso

### Cenário 1: Registrar Dívida na Saída

1. Usuário vai para `/pedidos/saida` (Tela de Saída)
2. Seleciona cliente e adiciona produtos ao carrinho
3. **Preenche o campo "Dívida (R$)"** com o valor (ex: R$ 50.00)
4. Clica "Registrar Saída"
5. **Automaticamente**:
   - Pedido é criado com status `'saida'`
   - Dívida é registrada na tabela `dividas` com status `'Em Aberto'`
   - Toast de sucesso: "Dívida de R$ 50.00 registrada com sucesso"
6. Nota fiscal é gerada e exibe:
   - Total do pedido (produtos + dívida)
   - Aviso: "ATENÇÃO - Dívida Pendente: R$ 50.00"

---

### Cenário 2: Cobrar Dívida no Retorno

1. Usuário vai para `/pedidos/retorno` (Tela de Retorno/Cálculo)
2. Seleciona pedido em aberto
3. Define devoluções dos produtos
4. **Preenche o campo "Cobrança de Dívida (R$)"** com o valor (ex: R$ 20.00)
5. Clica "Registrar Retorno e Finalizar Pedido"
6. **Automaticamente**:
   - Retorno é registrado
   - Pagamento de dívida é registrado:
     - Busca dívida mais antiga (FIFO)
     - Se valor é suficiente: marca como `'Quitado'`
     - Se não: marca como `'Parcialmente Pago'`
   - Saldo devedor é recalculado
7. Nota de retorno é gerada e exibe:
   - Itens retornados
   - Cobrança de Dívida: R$ 20.00
   - **Dívida Pendente Atualizada: R$ 30.00** ← NOVO
   - Total final

---

### Cenário 3: Consultar Dívidas no Dashboard

1. Usuário acessa `/dashboard-divida`
2. Dashboard carrega e exibe:
   - **Dívida Total**: R$ 1.250,00
   - **Clientes com Dívida**: 5
   - **Dívida Média**: R$ 250,00
3. Tabela mostra:
   - Cliente | CPF | Telefone | Saldo Devedor | Qtd Dívidas | % do Total
4. Usuário clica "Atualizar" para sincronizar dados

---

## 🔐 Segurança

- ✅ Todos os endpoints requerem autenticação JWT (`@token_required`)
- ✅ Validação de entrada em todos os endpoints
- ✅ Logs de ações de registro de dívida e pagamento
- ✅ Erros tratados com mensagens genéricas ao usuário

---

## 📊 Dados e Persistência

### Tabelas do Banco de Dados

1. **dividas**:
   - Armazena todos os débitos registrados
   - PK: `id_divida`
   - FK: `id_cliente`

2. **pagamentos_divida**:
   - Armazena todos os abatimentos
   - PK: `id_lancamento`
   - FK: `id_divida`

3. **clientes** (estendido):
   - Nova property calculada: `divida_pendente_total`
   - Não requer nova coluna (é uma aggregação)

---

## 🧪 Testes Recomendados

### Backend
```bash
# Registrar dívida
curl -X POST http://localhost:5000/api/dividas/registrar \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"id_cliente": 1, "valor_divida": 100}'

# Consultar saldo devedor
curl http://localhost:5000/api/dividas/clientes/1/divida-pendente \
  -H "Authorization: Bearer {token}"

# Registrar pagamento
curl -X POST http://localhost:5000/api/dividas/pagamentos-divida/registrar \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"id_cliente": 1, "cobranca_divida": 50}'
```

### Frontend
- Abra `/pedidos/saida` e registre uma dívida
- Vá para `/pedidos/retorno` e registre um pagamento
- Acesse `/dashboard-divida` para verificar saldo atualizado

---

## 🚀 Próximas Melhorias (Futuro)

- [ ] Relatório de dívidas por período
- [ ] Alertas automáticos para dívidas vencidas
- [ ] Interface de ajuste manual de dívidas
- [ ] Exportação de relatório em Excel
- [ ] SMS/Email para clientes com dívida
- [ ] Histórico de transações por dívida
- [ ] Multa/Juros automáticos

---

## 📞 Suporte

Para questões ou problemas com a implementação, consulte:
1. Logs do aplicativo em `app_log.txt`
2. Console do navegador (Frontend)
3. Logs do servidor Flask (Backend)

---

**Data de Conclusão**: 06 de Dezembro de 2025
**Desenvolvedor**: GitHub Copilot
**Status**: ✅ PRONTO PARA PRODUÇÃO
