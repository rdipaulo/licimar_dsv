# Guia Rápido de Instalação e Uso (v3)

Este guia assume que você está no diretório raiz do projeto (`licimar_dsv`).

## 1. Configuração do Backend (Python/Flask)

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

4. **Instale dependências adicionais (Windows):**
   ```bash
   pip install weasyprint
   ```
   *Necessário para geração de PDFs/Notas Fiscais.*

5. **Inicialize o Banco de Dados (SQLite):**
   ```bash
   python init_database.py
   ```
   *Isso criará o arquivo `instance/licimar_dev.db` e populará com dados de teste (incluindo admin/admin123).*

6. **Inicie o Servidor Backend:**

   **Opção A - Modo Normal (Recomendado):**
   ```bash
   set FLASK_DEBUG=0
   python app.py
   ```
   *O backend estará rodando em `http://localhost:5000`.*

   **Opção B - Modo Debug (Desenvolvimento):**
   ```bash
   python app.py
   ```
   *Ativa auto-reload de código, mas pode causar reinicializações frequentes.*

## 2. Configuração do Frontend (React/Vite)

1. **Navegue para o diretório do frontend:**
   ```bash
   cd ../../frontend/licimar_mvp_frontend
   ```

2. **Instale as dependências (Node.js/npm):**
   ```bash
   npm install --legacy-peer-deps
   ```
   *O `--legacy-peer-deps` é necessário para resolver conflitos de versão com `date-fns` e `react-day-picker`.*

3. **Configure a URL da API (Importante!):**
   Edite o arquivo `.env` e certifique-se de que a URL está correta:
   ```bash
   VITE_API_URL=http://localhost:5000
   ```
   *Isso garante que o frontend conecte corretamente ao backend local.*

4. **Inicie o Servidor Frontend:**
   ```bash
   npm run dev -- --host
   ```
   *O frontend estará rodando em `http://localhost:5173` (ou `http://localhost:5174` se a porta 5173 estiver ocupada).*

   > **Dica:** Você pode deixar o backend rodando em um terminal e o frontend em outro para desenvolvimento simultâneo.

## 3. Acesso ao Sistema

Abra seu navegador e acesse `http://localhost:5173` (ou `http://localhost:5174` se a porta anterior estiver em uso).

**Credenciais de Teste:**
- **Admin**: `admin` / `admin123`
- **Operador**: `operador` / `operador123`

> **Nota:** Certifique-se de que tanto o backend quanto o frontend estão rodando para que o sistema funcione corretamente.

## 4. Teste das Novas Funcionalidades

- **Atualização de Pedido**:
  1. Vá para **Registro de Saída**.
  2. Selecione um ambulante e adicione itens.
  3. **NÃO** finalize. Saia da página.
  4. Volte para **Registro de Saída** e selecione o mesmo ambulante. O pedido anterior será carregado para edição.

- **Restrição de Devolução (Gelo Seco)**:
  1. Crie um pedido de saída com **Gelo Seco**.
  2. Vá para **Registro de Retorno** e selecione o pedido.
  3. O campo de retorno para Gelo Seco estará desabilitado.

- **Impressão de Nota Fiscal**:
  1. A funcionalidade de impressão está implementada no backend (`GET /api/pedidos/<id>/imprimir`).
  2. No frontend, a integração do botão de impressão deve ser feita na tela de detalhes do pedido (que não foi criada, mas a função de API está pronta para ser usada).
  3. **Exemplo de uso da API (via navegador, após login):** `http://localhost:5000/api/pedidos/1/imprimir` (substitua 1 pelo ID do pedido).


Perfeito! Para os testes em Registro de Saída e Registro de Retorno, vou criar um script que:

Lista todos os pedidos (saída e retorno)
Permite deletar pedidos específicos após seus testes
Ou reseta tudo de uma vez
Deixa eu criar um script útil para você:

Created limpar_pedidos.py

Perfeito! Criei um script para você gerenciar os pedidos de teste. Agora você pode usar assim:

Listar todos os pedidos criados:
Deletar um pedido específico (por ID):
Deletar TODOS os pedidos de uma vez:
Como usar:

Faça seus testes em "Registro de Saída" e "Registro de Retorno"
Quando terminar, execute python limpar_pedidos.py listar para ver os IDs dos pedidos criados
Delete um por um com python limpar_pedidos.py deletar --id X
Ou delete todos com python limpar_pedidos.py limpar
Testa agora e me avisa quando quiser limpar!

