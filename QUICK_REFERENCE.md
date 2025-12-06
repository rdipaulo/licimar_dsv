# ⚡ QUICK REFERENCE - Comandos Essenciais

**Licimar MVP v2.0** | Últimas versão: 06/12/2025

---

## 🚀 Startup

### Backend
```bash
# Setup banco de dados (OBRIGATÓRIO na primeira vez)
cd backend/licimar_mvp_app
python setup_db.py

# Iniciar servidor Flask
python app.py
# Acesso: http://localhost:5000
```

### Frontend
```bash
# Instalar dependências (primeira vez)
cd frontend/licimar_mvp_frontend
npm install

# Iniciar dev server
npm run dev
# Acesso: http://localhost:5173
```

### Ambos (paralelo)
```bash
# Terminal 1: Backend
cd backend/licimar_mvp_app && python app.py

# Terminal 2: Frontend
cd frontend/licimar_mvp_frontend && npm run dev
```

---

## 🔐 Credenciais Padrão

| Campo | Valor |
|-------|-------|
| Username | admin |
| Password | admin123 |
| Role | admin |

---

## 📝 Configuração (.env)

### Backend
```env
FLASK_ENV=development
DATABASE_URL=sqlite:///instance/licimar_dev.db
JWT_SECRET_KEY=sua-chave-super-secreta
CORS_ORIGINS=*
```

### Frontend
```env
VITE_API_BASE_URL=http://localhost:5000
```

---

## 🔌 API Endpoints - Resumo Rápido

### Login
```bash
POST http://localhost:5000/api/auth/login
Body: {"username":"admin", "password":"admin123"}
```

### Pedidos
```bash
# Listar
GET /api/pedidos

# Criar saída
POST /api/pedidos/saida
Body: {
  "cliente_id": 1,
  "itens": [
    {"produto_id": 1, "quantidade_saida": 5}
  ]
}

# Registrar retorno
POST /api/pedidos/1/retorno
Body: {
  "itens": [
    {"produto_id": 1, "quantidade_retorno": 2}
  ],
  "divida": 25.50
}

# Gerar PDF
GET /api/pedidos/1/imprimir
GET /api/pedidos/1/imprimir_retorno
```

### Clientes
```bash
# Listar
GET /api/clientes

# Criar
POST /api/clientes
Body: {"nome": "Ivan Magé", "telefone": "21999999999"}

# Detalhes
GET /api/clientes/1

# Saldo devedor
GET /api/clientes/1/divida-total
```

### Produtos
```bash
# Listar
GET /api/produtos

# Criar (admin)
POST /api/produtos
Body: {
  "nome": "Picolé Chicabon",
  "preco": 2.50,
  "categoria_id": 1,
  "estoque": 100,
  "nao_devolve": false
}
```

### Dívidas
```bash
# Listar dívidas do cliente
GET /api/dividas/cliente/1

# Registrar nova dívida (admin)
POST /api/dividas
Body: {
  "id_cliente": 1,
  "valor_divida": 250.50,
  "descricao": "Dívida acumulada"
}

# Registrar pagamento
POST /api/pagamentos-divida
Body: {
  "id_divida": 1,
  "cobranca_divida": 50.00
}
```

---

## 🧹 Limpeza & Manutenção

### Reset do Banco
```bash
# Delete banco
rm backend/licimar_mvp_app/instance/licimar_dev.db

# Recrie
cd backend/licimar_mvp_app
python setup_db.py
```

### Limpar Cache
```bash
# Frontend
cd frontend/licimar_mvp_frontend
rm -r node_modules
npm install
```

---

## 📚 Documentação

| Documento | Propósito |
|-----------|----------|
| `README.md` | Quick start + overview |
| `ARQUITETURA_MATRIZ.md` | Documentação técnica completa |
| `CHANGELOG.md` | Histórico de versões |
| `IMPLEMENTACAO_COMPLETA.md` | Resumo da implementação |
| `QUICK_REFERENCE.md` | Este arquivo |

---

## 🔍 Troubleshooting Comum

### Erro: "No module named 'fpdf'"
```bash
pip install fpdf2
```

### Erro: "Database locked"
```bash
# Delete e recrie
rm backend/licimar_mvp_app/instance/licimar_dev.db
cd backend/licimar_mvp_app && python setup_db.py
```

### CORS Error
```bash
# Verifique .env
CORS_ORIGINS=*  # ou especifique origem
# Reinicie backend
```

### JWT Token expirado
```bash
# Faça login novamente
POST /api/auth/login
```

### Frontend não conecta no backend
```bash
# Verifique VITE_API_BASE_URL
# Backend deve estar rodando em :5000
# Frontend deve estar rodando em :5173
```

---

## 📊 Banco de Dados - 12 Tabelas

1. users - Usuários
2. clientes - Vendedores
3. categorias - Categorias
4. produtos - Produtos
5. regras_cobranca - Regras
6. pedidos - Pedidos
7. itens_pedido - Itens
8. dividas - Dívidas
9. pagamentos_divida - Pagamentos
10. pedidos_consignacao - Consignação
11. itens_pedido_consignacao - Itens consignação
12. logs - Auditoria

---

## 🔒 Headers Obrigatórios (Autenticado)

```bash
Authorization: Bearer <seu-jwt-token>
Content-Type: application/json
```

Exemplo:
```bash
curl -H "Authorization: Bearer eyJhbGc..." \
     -H "Content-Type: application/json" \
     http://localhost:5000/api/clientes
```

---

## 🎯 Fluxo Típico de Trabalho

### 1. Saída de Produtos
```
1. POST /api/pedidos/saida
   ├─ cliente_id
   ├─ itens (produto_id, quantidade)
   └─ Retorna: pedido_id

2. GET /api/pedidos/<pedido_id>/imprimir
   └─ Gera PDF
```

### 2. Retorno de Produtos
```
1. POST /api/pedidos/<pedido_id>/retorno
   ├─ itens (produto_id, quantidade_retorno)
   ├─ divida (opcional)
   └─ Retorna: pedido atualizado

2. GET /api/pedidos/<pedido_id>/imprimir_retorno
   └─ Gera PDF
```

### 3. Controle de Dívida
```
1. GET /api/dividas/cliente/<cliente_id>
   └─ Lista dívidas abertas

2. POST /api/pagamentos-divida
   ├─ id_divida
   ├─ cobranca_divida
   └─ Registra pagamento
```

---

## 💡 Tips & Tricks

### Ver logs da aplicação
```bash
# Backend
tail -f backend/licimar_mvp_app/logs.txt

# Frontend (console do navegador)
F12 → Console
```

### Debugar API
```bash
# Use Postman ou curl
curl http://localhost:5000/api/clientes

# Ou use VS Code REST Client
# Instale: REST Client extension
```

### Resetar sem deletar dados
```bash
# Se quer manter dados, edite setup_db.py
# Comente a linha de db.create_all()
# E mantenha apenas as linhas de INSERT
```

---

## 🚢 Deploy Checklist

- [ ] Variáveis de ambiente configuradas
- [ ] JWT_SECRET_KEY alterada
- [ ] Banco inicializado: `python setup_db.py`
- [ ] Backend em modo produção
- [ ] Frontend build: `npm run build`
- [ ] CORS_ORIGINS configurado
- [ ] SSL/HTTPS ativado
- [ ] Backups configurados

---

## 📞 Precisa de Ajuda?

1. **Documentação completa:** `ARQUITETURA_MATRIZ.md`
2. **Histórico de mudanças:** `CHANGELOG.md`
3. **Setup detalhado:** `README.md`
4. **Este documento:** `QUICK_REFERENCE.md`

---

## 🔄 Versão & Status

- **Versão:** 2.0
- **Status:** ✅ Production Ready
- **Última atualização:** 06/12/2025
- **Arquivo:** QUICK_REFERENCE.md
