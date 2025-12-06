# 📱 Licimar MVP - Sistema de Gerenciamento de Vendas

**Status:** ✅ Produção  
**Versão:** 2.0  
**Última Atualização:** 06/12/2025

## 📋 Sobre o Projeto

Licimar MVP é um sistema de gerenciamento de vendas e distribuição desenvolvido para vendedores ambulantes de sorvete e produtos congelados, com funcionalidades de:

- 📦 Registro de saída de produtos
- 🔄 Registro de retorno/devolução com automação
- 💰 Controle de dívidas e consignação
- 📄 Geração de PDFs de notas fiscais
- 📊 Dashboard com relatórios em tempo real
- 🔐 Autenticação JWT com controle de acesso

---

## 🚀 Quick Start

### Pré-requisitos
- Python 3.10+
- Node.js 18+
- Git


-- Orientação inicialização
# 1. Inicializar banco de dados
cd backend/licimar_mvp_app
python setup_db.py

# 2. Iniciar backend
python app.py

# 3. Em outro terminal, iniciar frontend
cd frontend/licimar_mvp_frontend
npm install
npm run dev

# 4. Acessar
http://localhost:5173


### Backend
```bash
# 1. Navegar para backend
cd backend/licimar_mvp_app

# 2. Criar e ativar venv
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 3. Instalar dependências
pip install -r requirements.txt
pip install fpdf2

# 4. Setup unificado do banco (ÚNICO script necessário)
python setup_db.py

# 5. Iniciar servidor
python app.py
```

Servidor rodará em: **http://localhost:5000**

### Frontend
```bash
# 1. Navegar para frontend
cd frontend/licimar_mvp_frontend

# 2. Instalar dependências
npm install

# 3. Iniciar dev server
npm run dev
```

Frontend rodará em: **http://localhost:5173**

---

## 📁 Estrutura do Projeto

```
licimar_dsv/
├── ARQUITETURA_MATRIZ.md           📄 Documentação completa
├── README.md                        📄 Este arquivo
├── CHANGELOG.md                     📄 Histórico de mudanças
│
├── backend/
│   └── licimar_mvp_app/
│       ├── src/
│       │   ├── main.py             # Flask app factory
│       │   ├── database.py         # Configuração BD
│       │   ├── models.py           # ⭐ 12 modelos SQLAlchemy
│       │   └── routes/             # Endpoints da API
│       ├── instance/
│       │   └── licimar_dev.db      # SQLite database
│       ├── setup_db.py             # 🎯 Setup unificado (ÚNICO)
│       ├── app.py                  # Entry point
│       └── requirements.txt        # Dependências
│
├── frontend/
│   └── licimar_mvp_frontend/
│       ├── src/
│       │   ├── pages/              # Telas da aplicação
│       │   ├── components/         # Componentes React
│       │   └── services/           # Cliente HTTP
│       ├── package.json
│       └── vite.config.ts
│
└── documentacao/                    # Documentação adicional
```

---

## 🔧 Stack Tecnológico

| Layer | Tecnologia | Versão |
|-------|-----------|--------|
| **Frontend** | React + TypeScript | 18.x + 5.x |
| **Build** | Vite | 5.x |
| **Styling** | Tailwind CSS | 3.x |
| **Backend** | Flask | 3.1.0 |
| **ORM** | SQLAlchemy | 2.0.40 |
| **Auth** | JWT | 4.6.0 |
| **PDF** | fpdf2 | 2.8.5 |
| **Database** | SQLite | 3.x |

---

## 💾 Base de Dados

### 12 Tabelas Principais

1. **users** - Usuários do sistema
2. **clientes** - Vendedores ambulantes
3. **categorias** - Categorias de produtos
4. **produtos** - Produtos disponíveis
5. **regras_cobranca** - Regras de cobrança automática
6. **pedidos** - Pedidos de saída/retorno
7. **itens_pedido** - Itens dos pedidos
8. **dividas** - Registro de dívidas
9. **pagamentos_divida** - Pagamentos e abatimentos
10. **pedidos_consignacao** - Pedidos em consignação
11. **itens_pedido_consignacao** - Itens de consignação
12. **logs** - Auditoria e logs

📄 **Veja documentação completa em:** `ARQUITETURA_MATRIZ.md`

---

## 🔌 API Endpoints

### Autenticação
```
POST   /api/auth/login
POST   /api/auth/refresh
POST   /api/auth/logout
```

### Pedidos
```
GET    /api/pedidos
POST   /api/pedidos/saida
POST   /api/pedidos/<id>/retorno
GET    /api/pedidos/<id>/imprimir
GET    /api/pedidos/<id>/imprimir_retorno
```

### Recursos
```
GET    /api/clientes
GET    /api/produtos
GET    /api/categorias
GET    /api/dividas/cliente/<cliente_id>
```

📄 **Veja lista completa em:** `ARQUITETURA_MATRIZ.md` (seção Endpoints)

---

## ⚙️ Configuração

### Variáveis de Ambiente

**Backend** (`.env`)
```env
FLASK_ENV=development
DATABASE_URL=sqlite:///instance/licimar_dev.db
JWT_SECRET_KEY=sua-chave-super-secreta-aqui
CORS_ORIGINS=*
```

**Frontend** (`.env.local`)
```env
VITE_API_BASE_URL=http://localhost:5000
```

---

## 💰 Sistema de Dívidas (NOVO)

### O que foi implementado
- ✅ Registro automatizado de dívidas na saída
- ✅ Cobrança de dívidas no retorno
- ✅ Cálculo automático de saldo devedor
- ✅ Quitação de dívidas com lógica FIFO (mais antiga primeiro)
- ✅ Dashboard de dívidas atualizado em tempo real
- ✅ Exibição de dívida pendente nas notas fiscais

### Endpoints Principais
```
GET    /api/dividas/clientes/{id}/divida-pendente    # Saldo devedor
POST   /api/dividas/registrar                          # Lançar dívida
POST   /api/dividas/pagamentos-divida/registrar        # Registrar pagamento
GET    /api/dividas                                   # Listar dívidas
```

### Telas Atualizadas
- `/pedidos/saida` - Campo "Dívida (R$)"
- `/pedidos/retorno` - Campo "Cobrança de Dívida (R$)"
- `/dashboard-divida` - Saldo devedor por cliente

### Documentação Completa
📄 **IMPLEMENTACAO_DIVIDAS_COMPLETA.md** - Guia técnico detalhado  
📄 **QUICK_REFERENCE_DIVIDAS.md** - Referência rápida  
📄 **ENDPOINTS_DIVIDAS.md** - Lista de endpoints com exemplos  
📄 **CHECKLIST_DIVIDAS.md** - Checklist completo de implementação

---

## 🎯 Fluxos Principais

### 1. Saída de Produtos
```
Vendedor → Registra Saída → Seleciona Produtos → 
[NOVO: Preenche Dívida (opcional)] → Calcula Total → Gera PDF → Sistema atualiza estoque
```

### 2. Retorno de Produtos
```
Vendedor → Registra Retorno → Informa Devoluções →
[NOVO: Cobra Dívida (opcional)] → Gera PDF → Finaliza Pedido
```

### 3. Controle de Dívidas (NOVO)
```
Dívida Original → Sistema → Registra como "Em Aberto"
Vendedor Paga → Sistema → Registra abatimento
Total Devedor = Σ(débito) - Σ(pagamentos)
Pagamento aplicado à dívida mais antiga (FIFO)
Se quitado → Status muda para "Quitado"
```

---

## ✅ Checklist de Deployment

- [ ] Variáveis de ambiente configuradas
- [ ] Banco de dados inicializado com `setup_db.py`
- [ ] JWT_SECRET_KEY alterada para valor seguro
- [ ] CORS_ORIGINS configurado corretamente
- [ ] Frontend build: `npm run build`
- [ ] Backend em modo produção
- [ ] SSL/HTTPS ativado
- [ ] Backups configurados

---

## 📊 Status Atual

### ✅ Implementado
- ✓ Sistema de autenticação JWT
- ✓ Saída e retorno de produtos
- ✓ Geração de PDFs
- ✓ Cobrança de dívida discriminada
- ✓ Modelos Dívida/Consignação
- ✓ Dashboard com relatórios
- ✓ Controle de produtos não-devolve (gelo seco)
- ✓ Integração frontend/backend

### 🔄 Em Desenvolvimento
- Relatórios avançados
- Integração com sistemas externos

### 📋 Backlog
- Aplicativo mobile
- Sincronização offline
- Análise preditiva

---

## 🐛 Troubleshooting

### Erro: "No module named 'fpdf'"
```bash
pip install fpdf2
```

### Erro: "Database locked"
```bash
# Delete e recrie o banco
rm backend/licimar_mvp_app/instance/licimar_dev.db
cd backend/licimar_mvp_app
python setup_db.py
```

### CORS Error
- Verifique `CORS_ORIGINS` no `.env`
- Reinicie backend e frontend

### JWT Token expirado
- Faça login novamente
- Token será renovado automaticamente

---

## 📚 Documentação Adicional

- 📖 **ARQUITETURA_MATRIZ.md** - Documentação técnica completa
- 📝 **CHANGELOG.md** - Histórico de mudanças
- 📋 **documentacao/** - Documentação de negócios

---

## 👥 Equipe

**Desenvolvimento:** Licimar MVP Team  
**Última atualização:** 06/12/2025  
**Versão:** 2.0

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte a documentação em `ARQUITETURA_MATRIZ.md`
2. Verifique o `CHANGELOG.md` para mudanças recentes
3. Rode `setup_db.py` para reinicializar o banco

---

## 🔒 Segurança

- ✅ Autenticação JWT
- ✅ Hashe de senhas com Werkzeug
- ✅ CORS configurável
- ✅ Logs de auditoria
- ✅ Validação de entrada

---

**Projeto desenvolvido com ❤️ para vendedores ambulantes**
