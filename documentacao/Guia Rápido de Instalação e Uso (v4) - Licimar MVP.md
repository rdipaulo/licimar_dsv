# Guia Rápido de Instalação e Uso (v4) - Licimar MVP

Este guia foi atualizado para refletir as correções e refatorações realizadas na aplicação, incluindo a mudança de `Ambulante` para `Cliente` e a preparação para deploy em produção.

Este guia assume que você está no diretório raiz do projeto (`licimar_dsv`).

## 1. Configuração do Backend (Python/Flask)

O backend foi preparado para ser executado tanto em ambiente de desenvolvimento (SQLite) quanto em produção (PostgreSQL/MySQL).

1. **Navegue para o diretório do backend:**
   ```bash
   cd backend/licimar_mvp_app
   ```

2. **Crie e ative o ambiente virtual:**
   ```bash
   python3 -m venv venv
   . venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```
   *As dependências de produção (como `psycopg2-binary` para PostgreSQL e `weasyprint` para PDF) já estão incluídas.*

4. **Configuração de Ambiente:**
   Crie um arquivo `.env` na pasta `backend/licimar_mvp_app` para configurar o ambiente.

   **Para Desenvolvimento (SQLite):**
   ```ini
   # Arquivo: .env
   FLASK_ENV=development
   SECRET_KEY=sua_chave_secreta_aqui
   # DATABASE_URL não é necessário para SQLite local
   ```

   **Para Produção (Exemplo com PostgreSQL):**
   ```ini
   # Arquivo: .env
   FLASK_ENV=production
   SECRET_KEY=sua_chave_secreta_aqui_e_longa
   DATABASE_URL=postgresql://usuario:senha@host:porta/nome_do_banco
   ```
   *Para produção, a variável `DATABASE_URL` deve ser configurada com a string de conexão do seu banco de dados (PostgreSQL, MySQL, etc.).*

5. **Inicialize o Banco de Dados:**
   ```bash
   python init_database.py
   ```
   *Este script criará o banco de dados e populará com dados de teste **apenas se o banco estiver vazio**, garantindo a persistência (Correção 1).*

6. **Inicie o Servidor Backend:**
   ```bash
   python app.py
   ```
   *O backend estará rodando em `http://localhost:5000`.*

## 2. Configuração do Frontend (React/Vite)

O frontend foi refatorado para usar `Cliente` em vez de `Ambulante` e está pronto para ser parametrizado.

1. **Navegue para o diretório do frontend:**
   ```bash
   cd ../../frontend/licimar_mvp_frontend
   ```

2. **Instale as dependências (Node.js/pnpm):**
   ```bash
   pnpm install
   ```
   *O projeto utiliza `pnpm`. Se preferir `npm`, use `npm install --legacy-peer-deps`.*

3. **Configure a URL da API (Parametrização):**
   Crie um arquivo `.env.local` na pasta `frontend/licimar_mvp_frontend` para configurar a URL do backend.

   **Para Desenvolvimento (Conectando ao Backend Local):**
   ```ini
   # Arquivo: .env.local
   VITE_API_URL=http://localhost:5000/api
   ```

   **Para Produção (Conectando ao Backend Publicado):**
   ```ini
   # Arquivo: .env.local
   VITE_API_URL=https://sua-api-licimar.com.br/api
   ```
   *A URL deve apontar para o endpoint `/api` do seu backend publicado.*

4. **Inicie o Servidor Frontend:**
   ```bash
   pnpm run dev -- --host
   ```
   *O frontend estará rodando em `http://localhost:5173` (ou porta similar).*

## 3. Acesso ao Sistema e Novas Credenciais

Abra seu navegador e acesse a URL do frontend (ex: `http://localhost:5173`).

| Credencial | Login | Senha | Observação |
| :--- | :--- | :--- | :--- |
| **Administrador** | `licimar` | `licim@r2025&&` | **NOVAS CREDENCIAIS**. A senha é armazenada com hash bcrypt. |
| **Operador** | `operador` | `operador123` | Credenciais de teste padrão. |

## 4. Instruções para Deploy em Produção

O projeto está configurado para deploy em plataformas que suportam Procfile (como Heroku ou Railway).

### Backend (Python/Flask)

1.  **Arquivos Chave:** `Procfile`, `requirements.txt`, `runtime.txt` e `app.py` foram atualizados.
2.  **Servidor WSGI:** O `Procfile` usa **Gunicorn** para servir a aplicação de forma robusta:
    ```
    web: gunicorn --bind 0.0.0.0:$PORT --timeout 60 --workers 4 app:app
    ```
3.  **Variáveis de Ambiente:** **É obrigatório** configurar as seguintes variáveis no seu ambiente de deploy:
    *   `FLASK_ENV=production`
    *   `SECRET_KEY` (chave longa e única)
    *   `DATABASE_URL` (string de conexão do seu banco de dados de produção)

### Frontend (React/Vite)

1.  **Build:** O frontend deve ser construído antes do deploy:
    ```bash
    pnpm run build
    ```
2.  **Variável de Ambiente:** **É obrigatório** configurar a variável de ambiente `VITE_API_URL` no seu ambiente de build/deploy do frontend, apontando para a URL pública do seu backend (ex: `https://sua-api-licimar.com.br/api`).
3.  **Serviço:** O diretório `dist` gerado pelo build deve ser servido por um servidor estático (como Nginx ou o serviço de hospedagem de frontend da sua plataforma).

## 5. Teste das Funcionalidades Corrigidas

As seguintes correções foram implementadas e podem ser testadas:

| Correção | Descrição | Teste de Validação |
| :--- | :--- | :--- |
| **Refatoração** | `Ambulante` renomeado para `Cliente` em todo o sistema. | Navegue para a página de Clientes e verifique se a listagem e o CRUD funcionam. |
| **Persistência DB** | `init_database.py` não sobrescreve dados existentes. | Execute `python init_database.py` novamente; os dados não devem ser duplicados. |
| **Inserção de Produtos** | Validação de cliente ativo antes de criar pedido. | Tente criar um pedido sem selecionar um cliente. |
| **Campo de Retorno** | Validação de quantidade de retorno ≤ quantidade de saída. | Crie um pedido de saída e, no retorno, tente devolver mais do que saiu. |
| **Cobrança de Dívida** | `divida_acumulada` do cliente é atualizada no retorno. | Crie um pedido com dívida no retorno e verifique o campo `Dívida Acumulada` do cliente. |
| **Impressão/Layout** | Rotas de impressão prontas para gerar PDFs. | Após finalizar um pedido, use a rota de API (ex: `http://localhost:5000/api/pedidos/1/imprimir`) para verificar a geração do PDF. |
