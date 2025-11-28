# Licimar MVP - Guia Completo de Setup & Deployment

## Status Atual ✅

**Aplicação totalmente funcional!**
- Backend (Python/Flask): http://localhost:5000
- Frontend (React/Vite): http://localhost:5174
- Banco de dados SQLite: Persistente e funcional
- Autenticação JWT: Implementada e testada

## 1. Setup Rápido (Local)

### Opção A: Setup Automático (Recomendado)
```bash
# Na raiz do projeto
python setup.py
```

### Opção B: Setup Manual

#### Backend
```bash
cd backend/licimar_mvp_app
pip install -r requirements.txt
pip install weasyprint  # Necessário para PDF/Notas Fiscais
python init_database.py  # Cria banco e dados de teste
python app.py            # Inicia servidor
```

#### Frontend (em outro terminal)
```bash
cd frontend/licimar_mvp_frontend
npm install --legacy-peer-deps
npm run dev -- --host
```

## 2. Credenciais de Teste

```
Admin:
  - Usuário: admin
  - Senha: admin123
  - Acesso: Todos os recursos

Operador:
  - Usuário: operador
  - Senha: operador123
  - Acesso: Apenas Registro de Saída
```

## 3. Funcionalidades Implementadas

### ✅ Registro de Saída (Saída de Produtos)
- Selecione ambulante e produtos
- Informe quantidade/peso (para gelo seco)
- Registre data/hora
- **Impressão de Nota de Saída** com PDF

### ✅ Registro de Retorno (Devolução de Produtos)
- Carregue pedido de saída anterior
- Registre devoluções e perdas
- **Impressão de Nota de Retorno** com PDF
- Gelo seco bloqueado para devolução (restrição)

### ✅ Gestão de Ambulantes
- Cadastro, edição, exclusão
- **Rastreamento de Dívida Acumulada** (divida_acumulada)
- Visualização de histórico

### ✅ Gestão de Produtos
- Cadastro com **campo Peso** para produtos como gelo seco
- Categorias de produtos
- Preços e estoques

### ✅ Dashboard de Dívida
- Visão geral de dívidas por ambulante
- Total acumulado
- Porcentagem de contribuição

### ✅ Histórico de Pedidos
- Visualizar todos os pedidos
- Reimprimir notas fiscais
- Filtrar por status

### ✅ Autenticação & Segurança
- Login com JWT tokens
- Tokens armazenados em localStorage (frontend)
- Autorização por role (admin/operador)
- Tokens com expiração configurável

## 4. Stack Tecnológico

### Backend
- **Python** 3.13
- **Flask** 3.1.0 - Framework web
- **SQLAlchemy** 2.0.40 - ORM para banco de dados
- **Flask-JWT-Extended** - Autenticação JWT
- **Flask-CORS** - CORS para chamadas do frontend
- **WeasyPrint** - Geração de PDFs
- **SQLite** - Banco de dados local

### Frontend
- **React** 18
- **TypeScript** - Type safety
- **Vite** 6.4.1 - Build tool
- **React Router** - Navegação
- **TailwindCSS** - Styling
- **SonnerToast** - Notificações
- **Axios** - HTTP client

### DevOps
- **Docker & Docker Compose** - Containerização
- **Nginx** - Proxy reverso (produção)
- **Gunicorn** - WSGI server (produção)

## 5. Estrutura do Banco de Dados

### Tabelas Principais

#### ambulantes
```
id, nome, telefone, email, cpf, endereco, status, created_at, updated_at, divida_acumulada
```

#### produtos
```
id, nome, categoria_id, preco, peso, estoque, created_at, updated_at
```

#### categorias
```
id, nome, descricao, created_at, updated_at
```

#### pedidos
```
id, ambulante_id, data, hora, status, items (JSON), total, divida_gerada, created_at, updated_at
```

#### usuarios
```
id, username, email, password_hash, role (admin/operador), active, created_at, updated_at
```

## 6. API Endpoints

### Autenticação
```
POST /api/auth/login                 - Login
POST /api/auth/refresh               - Refresh token
GET  /api/auth/me                    - Perfil do usuário
```

### Ambulantes
```
GET    /api/ambulantes               - Listar todos
GET    /api/ambulantes/<id>          - Detalhe
POST   /api/ambulantes               - Criar
PUT    /api/ambulantes/<id>          - Atualizar (incluindo divida_acumulada)
DELETE /api/ambulantes/<id>          - Deletar
```

### Produtos
```
GET    /api/produtos                 - Listar todos
GET    /api/produtos/<id>            - Detalhe
POST   /api/produtos                 - Criar
PUT    /api/produtos/<id>            - Atualizar (incluindo peso)
DELETE /api/produtos/<id>            - Deletar
```

### Pedidos
```
GET    /api/pedidos                  - Listar todos
GET    /api/pedidos/<id>             - Detalhe
POST   /api/pedidos                  - Criar novo
PUT    /api/pedidos/<id>             - Atualizar
GET    /api/pedidos/<id>/imprimir    - Baixar PDF (Nota de Saída)
GET    /api/pedidos/<id>/imprimir_retorno - Baixar PDF (Nota de Retorno)
```

### Categorias
```
GET    /api/categorias               - Listar todas
POST   /api/categorias               - Criar
```

## 7. Deployment com Docker (Produção)

### Build das imagens
```bash
docker-compose -f docker-compose.prod.yml build
```

### Iniciar containers
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Configuração de ambiente (.env.production)
```
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here
DATABASE_URL=sqlite:////data/licimar.db
VITE_API_URL=https://seu-dominio.com
```

### Acessar em produção
```
https://seu-dominio.com
```

## 8. Dados Persistentes em Docker

O banco de dados SQLite é armazenado em um **volume Docker** chamado `licimar_data`:

```bash
# Ver volumes
docker volume ls

# Inspecionar volume
docker volume inspect licimar_dsv_licimar_data

# Backup do banco
docker run --rm -v licimar_dsv_licimar_data:/data -v $(pwd):/backup \
  busybox cp /data/licimar.db /backup/

# Restaurar banco
docker run --rm -v licimar_dsv_licimar_data:/data -v $(pwd):/backup \
  busybox cp /backup/licimar.db /data/
```

## 9. Troubleshooting

### Backend não inicia
```bash
# Verificar logs
docker-compose -f docker-compose.prod.yml logs backend

# Testar localmente
cd backend/licimar_mvp_app
python app.py

# Health check
curl http://localhost:5000/api/health
```

### Frontend não conecta ao backend
- Verificar VITE_API_URL em `.env`
- Verificar CORS no backend
- Inspecionar Network no DevTools (F12)

### Banco de dados corrompido
```bash
# Reinicializar banco em desenvolvimento
rm backend/licimar_mvp_app/instance/licimar_dev.db
cd backend/licimar_mvp_app
python init_database.py
```

### PDF de Notas Fiscais não gera
- Verificar se WeasyPrint está instalado
- Verificar permissões de arquivo
- Verificar logs do backend

## 10. Monitoramento (Produção)

### Logs
```bash
# Backend
docker logs -f licimar_backend

# Frontend
docker logs -f licimar_frontend

# Nginx
docker logs -f licimar_frontend  # nginx roda no mesmo container
```

### Health Checks
```bash
# API
curl http://localhost:5000/api/health

# Status detalhado
curl http://localhost:5000/api/status
```

## 11. Atualizações & Migrações

### Adicionar nova coluna ao banco
```bash
# 1. Criar migration em backend/licimar_mvp_app/
# 2. Executar migração
python <migration_file>.py

# 3. Reiniciar containers (se Docker)
docker-compose -f docker-compose.prod.yml restart backend
```

### Atualizar dependências
```bash
# Backend
cd backend/licimar_mvp_app
pip install --upgrade -r requirements.txt

# Frontend
cd frontend/licimar_mvp_frontend
npm update
```

## 12. Performance & Otimizações

### Backend
- Gunicorn com múltiplos workers em produção
- Cache de queries (implementar conforme necessário)
- Índices no banco de dados para ambulantes, pedidos

### Frontend
- Code splitting automático com Vite
- Lazy loading de rotas
- Minificação em produção

### Banco de Dados
- SQLite adequado para pequenos volumes (<100GB)
- Para escalar: migrar para PostgreSQL
- Backup regular recomendado

## 13. Configuração de Hosting Recomendado

### Opções Baratas/Gratuitas
1. **Render.com** - Free tier, $7/mês depois
2. **Railway.app** - $5-10/mês
3. **Replit.com** - Free com limitações
4. **PythonAnywhere** - $5/mês

### Configuração Render.com (exemplo)
```yaml
# Criar 2 serviços:
# 1. Web Service (Frontend + Backend em nginx)
# 2. Background Worker (se necessário para PDF generation)

# Environment variables
FLASK_ENV=production
SECRET_KEY=<gerar-chave-segura>
JWT_SECRET=<gerar-jwt-seguro>
```

## 14. Checklist Final de Produção

- [ ] Mudar SECRET_KEY e JWT_SECRET em .env.production
- [ ] Configurar domínio (CORS_ORIGINS)
- [ ] Configurar SSL/TLS (certificado Let's Encrypt)
- [ ] Fazer backup do banco de dados
- [ ] Verificar limites de upload (máx 20MB)
- [ ] Testar login com credenciais reais (não admin)
- [ ] Testar geração de PDFs
- [ ] Monitorar logs nos primeiros dias
- [ ] Configurar alertas de erro
- [ ] Documentar senha de admin (armazenar seguro)
- [ ] Implementar 2FA para admin (opcional)

## 15. Suporte & Debugging

### Logs detalhados
```bash
# Backend com debug
FLASK_DEBUG=1 python app.py

# Frontend
npm run dev -- --debug
```

### Testes automáticos
```bash
# Backend
cd backend/licimar_mvp_app
python test_quick.py

# Frontend (quando implementado)
cd frontend
npm run test
```

---

**Última atualização:** 28/11/2025
**Versão:** 2.0.0
**Status:** Production Ready ✅
