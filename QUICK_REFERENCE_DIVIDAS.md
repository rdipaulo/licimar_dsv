# 🚀 Quick Reference - Implementação de Dívidas

## 📚 Arquivos Modificados

### Backend
- `src/main.py` - Registrado blueprint de dividas
- `src/routes/dividas.py` - 3 endpoints implementados + 1 adicional
- `src/models.py` - Models existentes, property adicionada
- `src/routes/pedidos.py` - Notas fiscais atualizadas

### Frontend
- `src/services/api.ts` - 4 métodos de API adicionados
- `src/pages/Pedidos/PedidosSaida.tsx` - Campo "Dívida" adicionado
- `src/pages/Pedidos/PedidosRetorno.tsx` - Registro de pagamento adicionado
- `src/pages/DashboardDivida.tsx` - Lógica atualizada

---

## 🔌 Endpoints da API

| Método | Path | Função | Auth |
|--------|------|--------|------|
| GET | `/api/dividas/clientes/{id}/divida-pendente` | Saldo devedor | JWT ✅ |
| POST | `/api/dividas/registrar` | Lançar dívida | JWT ✅ |
| POST | `/api/dividas/pagamentos-divida/registrar` | Registrar pagamento | JWT ✅ |
| GET | `/api/dividas` | Listar dívidas | JWT ✅ |

---

## 💡 Exemplos de Uso

### 1. Registrar Dívida (Backend)
```bash
POST /api/dividas/registrar
Authorization: Bearer {token}

{
  "id_cliente": 1,
  "valor_divida": 250.00,
  "descricao": "Dívida do Pedido de Saída #123"
}
```

### 2. Registrar Pagamento (Backend)
```bash
POST /api/dividas/pagamentos-divida/registrar
Authorization: Bearer {token}

{
  "id_cliente": 1,
  "cobranca_divida": 100.00,
  "descricao": "Cobrança do Pedido de Retorno #456"
}
```

### 3. Consultar Dívida Pendente (Backend)
```bash
GET /api/dividas/clientes/1/divida-pendente
Authorization: Bearer {token}
```

**Response**:
```json
{
  "cliente_id": 1,
  "cliente_nome": "João Silva",
  "divida_total": 500.00,
  "cobrancas_total": 100.00,
  "saldo_devedor": 400.00,
  "quantidade_dividas": 3
}
```

---

## 🎯 Fluxo na Interface

### Tela de Saída (`/pedidos/saida`)
```
[Selecionar Cliente] → [Adicionar Produtos] → [NOVO: Preencher Dívida (R$)]
                                              ↓
                                      [Registrar Saída]
                                              ↓
                      Pedido criado + Dívida registrada automaticamente
```

### Tela de Retorno (`/pedidos/retorno`)
```
[Selecionar Pedido] → [Devolver Produtos] → [NOVO: Preencher Cobrança de Dívida (R$)]
                                            ↓
                                    [Registrar Retorno]
                                            ↓
                      Pagamento registrado + Nota impressa com Dívida Pendente
```

### Dashboard (`/dashboard-divida`)
```
[Carregar Dados] → [Consultar getDividaPendente() por cliente]
                           ↓
            Exibir saldo devedor atualizado para cada cliente
```

---

## 🔧 Tecnologias

- **Backend**: Flask + SQLAlchemy + JWT
- **Frontend**: React + TypeScript + Tailwind CSS
- **Database**: SQLite (desenvolvimento)
- **PDF**: fpdf2 (geração de notas)

---

## ✨ Destaques da Implementação

✅ **Cálculo Automático**: Saldo devedor calculado via property `@property divida_pendente_total`
✅ **Fila FIFO**: Pagamentos aplicados à dívida mais antiga primeiro
✅ **Integração Automática**: Dívida registrada ao finalizar saída
✅ **Impressão**: Nota de retorno mostra dívida pendente atualizada
✅ **Dashboard**: Consulta dívida atual via API endpoint
✅ **Validações**: Todos os inputs validados (client + server)
✅ **Logs**: Todas as ações de dívida registradas para auditoria

---

## ⚠️ Casos Especiais

### Quando há dívida no campo de saída
→ Automaticamente registra no endpoint `/api/dividas/registrar`

### Quando há cobrança no campo de retorno
→ Automaticamente registra no endpoint `/api/dividas/pagamentos-divida/registrar`

### Quando o pagamento supera a dívida atual
→ Marca dívida como 'Quitado' e passa para próxima (se houver)

### Quando não há dívida aberta
→ Endpoint retorna erro 400 "Cliente não possui dívidas em aberto"

---

## 📊 Status das Dívidas

| Status | Significado |
|--------|-------------|
| `Em Aberto` | Dívida total não foi abatida |
| `Parcialmente Pago` | Parte da dívida foi abatida |
| `Quitado` | Dívida foi totalmente abatida |

---

## 🐛 Troubleshooting

### Dívida não aparece no Dashboard
→ Verificar se dívida foi registrada no endpoint correto
→ Testar GET `/api/dividas/clientes/{id}/divida-pendente`

### Pagamento não desconta saldo
→ Verificar se cliente_id está correto
→ Verificar se há dívida aberta para o cliente

### Nota fiscal sem "Dívida Pendente"
→ Verificar se cliente tem saldo_devedor > 0
→ Nota de saída mostra aviso, retorno mostra valor

---

## 📞 Debug Mode

Ativar logs com:
```python
# Backend
current_app.logger.info(f"[DEBUG] Dívida registrada: {divida_id}")

# Frontend
console.log('[DEBUG] Dívida registrada:', response);
```

---

## ✅ Checklist de Validação

- [ ] Backend rodando em `http://localhost:5000`
- [ ] Frontend rodando em `http://localhost:5173`
- [ ] Endpoint GET `/api/dividas/clientes/1/divida-pendente` respondendo
- [ ] Endpoint POST `/api/dividas/registrar` criando dívida
- [ ] Endpoint POST `/api/dividas/pagamentos-divida/registrar` funcionando
- [ ] Campo "Dívida" visível em `/pedidos/saida`
- [ ] Campo "Cobrança de Dívida" visível em `/pedidos/retorno`
- [ ] Dashboard mostrando saldos corretos
- [ ] Nota fiscal exibindo "Dívida Pendente"

---

**Última atualização**: 06 de Dezembro de 2025
