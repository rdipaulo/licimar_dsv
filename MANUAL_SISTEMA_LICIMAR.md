# Manual do Sistema Licimar - Boas Práticas e Orientações de Desenvolvimento

## Introdução

Este documento serve como um guia abrangente para o sistema Licimar, detalhando as melhorias implementadas, as boas práticas de desenvolvimento adotadas e as orientações para futuras manutenções, desenvolvimentos e operações. O objetivo é garantir a robustez, escalabilidade e manutenibilidade da aplicação, promovendo um ciclo de vida de desenvolvimento eficiente e seguro.

## 1. Aplicação das Alterações (Pull Request)

Para integrar as melhorias desenvolvidas neste projeto ao seu repositório original no GitHub, siga os passos abaixo. Este processo garante que você tenha controle total sobre as alterações e possa revisá-las antes de mesclá-las.

### 1.1. Pré-requisitos

Certifique-se de ter o Git instalado e configurado em sua máquina local.

### 1.2. Clonar o Repositório Original (se ainda não o fez)

Se você ainda não tem uma cópia local do seu repositório original, clone-o:

```bash
git clone https://github.com/rdipaulo/licimar_dsv.git
cd licimar_dsv
```

### 1.3. Adicionar o Repositório com as Alterações como um Remote

Para facilitar a obtenção das minhas alterações, você pode adicionar o repositório que contém as melhorias como um *remote* temporário. **Atenção:** Este passo é apenas para fins de demonstração, pois o repositório que eu criei é local e não pode ser acessado diretamente por você. O ideal é que eu forneça as alterações via um arquivo compactado ou que você crie um novo branch no seu repositório e eu forneça as instruções para aplicar as alterações diretamente nele.

**Considerando que você está no diretório `licimar_dsv` do seu projeto:**

### 1.4. Aplicar as Alterações

Como não é possível fazer um `git pull` diretamente de um repositório local meu, a melhor abordagem é que você crie um novo branch no seu repositório e eu forneça um patch ou as instruções para copiar os arquivos alterados. Para este cenário, vou listar os arquivos alterados e você pode copiá-los manualmente para o seu projeto, ou criar um patch.

**Opção 1: Copiar arquivos manualmente (Recomendado para este caso)**

Você pode baixar o projeto completo que eu modifiquei (será fornecido como um arquivo `.zip` ou similar) e copiar os arquivos para as respectivas pastas no seu projeto. **ATENÇÃO:** Esta é a forma mais direta, mas exige cuidado para não sobrescrever arquivos que você possa ter modificado localmente e que não foram considerados nas minhas alterações.

**Opção 2: Criar um patch (Mais técnico, mas mais seguro para mesclagem)**

1.  **No meu ambiente (simulado):** Eu geraria um patch com as alterações.
    ```bash
git diff master > changes.patch
    ```
2.  **No seu ambiente:** Você aplicaria o patch no seu branch de desenvolvimento.
    ```bash
git apply changes.patch
    ```

### 1.5. Criar um Novo Branch para as Alterações

É crucial trabalhar em um branch separado para as novas funcionalidades e melhorias. Isso permite que você revise, teste e, se necessário, descarte as alterações sem afetar a linha principal de desenvolvimento (`main` ou `master`).

```bash
git checkout -b feature/refatoracao-licimar
```

### 1.6. Adicionar e Commitar as Alterações

Após copiar os arquivos ou aplicar o patch, adicione-os ao *staging area* e crie um commit:

```bash
git add .
git commit -m "feat: Implementação completa do backend e estrutura inicial do frontend com boas práticas"
```

### 1.7. Enviar para o GitHub

Envie o novo branch para o seu repositório no GitHub:

```bash
git push -u origin feature/refatoracao-licimar
```

### 1.8. Abrir um Pull Request (PR)

1.  Acesse o seu repositório no GitHub. Você verá uma notificação sugerindo a abertura de um Pull Request para o branch `feature/refatoracao-licimar`.
2.  Clique em 

"Compare & pull request" ou navegue até a aba "Pull requests" e clique em "New pull request".
3.  Selecione o branch `feature/refatoracao-licimar` como `compare` e o seu branch principal (`main` ou `master`) como `base`.
4.  Preencha o título e a descrição do Pull Request, detalhando as alterações realizadas.
5.  Crie o Pull Request e aguarde a revisão (se houver) e a mesclagem.

## 2. Boas Práticas de Desenvolvimento

Para garantir a robustez e a manutenibilidade do sistema, as seguintes boas práticas foram adotadas e devem ser seguidas em desenvolvimentos futuros:

### 2.1. Backend (Flask)

*   **Estrutura Modular:** O backend foi organizado em blueprints (módulos) para cada recurso (ambulantes, produtos, usuários, etc.), facilitando a organização, manutenção e escalabilidade. Novos recursos devem seguir essa estrutura.
*   **Validação de Dados:** Todas as entradas de dados da API são validadas rigorosamente para prevenir injeção de SQL, XSS e outros ataques, além de garantir a integridade dos dados. Utilize bibliotecas como `Marshmallow` ou validação manual robusta.
*   **Autenticação e Autorização (JWT):** Implementação de JSON Web Tokens (JWT) para autenticação segura. Os endpoints são protegidos por decoradores (`@token_required`, `@admin_required`) para garantir que apenas usuários autorizados acessem os recursos. Mantenha as chaves JWT seguras e rotacione-as periodicamente.
*   **Tratamento de Erros Centralizado:** Erros são tratados de forma consistente com `errorhandler` no `main.py`, retornando mensagens de erro padronizadas e códigos de status HTTP apropriados.
*   **Logging:** O sistema registra ações importantes (`@log_action`) e erros, facilitando a depuração e auditoria. Utilize o módulo `logging` do Python para registrar eventos relevantes.
*   **Configuração de Ambiente:** Uso de variáveis de ambiente (`.env`) para configurações sensíveis (chaves secretas, credenciais de banco de dados), garantindo que não sejam expostas no código-fonte. O arquivo `.env.example` serve como template.
*   **Banco de Dados (SQLAlchemy):** Utilização de SQLAlchemy ORM para interação com o banco de dados, abstraindo a lógica SQL e facilitando a manipulação de objetos. Migrações de banco de dados devem ser gerenciadas com `Flask-Migrate` ou similar.
*   **Testes Unitários e de Integração:** Para garantir a qualidade do código, é fundamental escrever testes unitários para as funções e testes de integração para os endpoints da API. (Não implementado nesta fase, mas altamente recomendado para futuras melhorias).

### 2.2. Frontend (React com TypeScript)

*   **Componentização:** O frontend é construído com componentes React reutilizáveis, seguindo o princípio de responsabilidade única. Novos componentes devem ser criados com foco na reusabilidade e modularidade.
*   **Tipagem (TypeScript):** A utilização de TypeScript garante maior segurança e previsibilidade ao código, detectando erros em tempo de desenvolvimento. Todos os novos códigos devem ser tipados.
*   **Gerenciamento de Estado (Context API/Redux/Zustand):** Para o gerenciamento de estado global (como autenticação), foi utilizado o Context API. Para aplicações maiores, considere Redux ou Zustand.
*   **Serviço de API Centralizado:** Todas as chamadas à API são encapsuladas em um `ApiService`, facilitando a manutenção e a padronização das requisições HTTP.
*   **Roteamento (React Router DOM):** Utilização de `react-router-dom` para gerenciar as rotas da aplicação, incluindo rotas protegidas por autenticação e autorização (`ProtectedRoute`).
*   **UI Components (Shadcn/UI):** Uso de uma biblioteca de componentes UI (Shadcn/UI) para garantir consistência visual e acelerar o desenvolvimento da interface. Mantenha a padronização visual.
*   **Validação de Formulários:** Utilize bibliotecas como `react-hook-form` com `Zod` para validação robusta de formulários.
*   **Tratamento de Erros e Notificações:** Erros de API são tratados e exibidos ao usuário através de componentes de notificação (`toast`).
*   **Variáveis de Ambiente:** Uso de `VITE_API_URL` para configurar a URL da API, permitindo fácil troca entre ambientes de desenvolvimento e produção.

## 3. Estrutura do Projeto

A estrutura do projeto foi organizada para separar claramente o backend e o frontend, além de modularizar cada parte internamente.

```
licimar_dsv/
├── backend/
│   └── licimar_mvp_app/
│       ├── .env.example             # Exemplo de variáveis de ambiente
│       ├── init_database.py         # Script para inicializar o banco de dados
│       ├── requirements.txt         # Dependências do Python
│       └── src/
│           ├── config.py            # Configurações da aplicação Flask
│           ├── database.py          # Configuração do SQLAlchemy
│           ├── main.py              # Aplicação Flask principal
│           ├── models.py            # Modelos do banco de dados (SQLAlchemy)
│           ├── routes/              # Blueprints para cada recurso da API
│           │   ├── ambulantes.py
│           │   ├── auth.py
│           │   ├── categorias.py
│           │   ├── logs.py
│           │   ├── pedidos.py
│           │   ├── produtos.py
│           │   ├── regras_cobranca.py
│           │   ├── relatorios.py
│           │   └── usuarios.py
│           └── utils/               # Utilitários e helpers
│               ├── decorators.py
│               └── helpers.py
├── frontend/
│   └── licimar_mvp_frontend/
│       ├── public/
│       ├── src/
│       │   ├── assets/              # Imagens e outros ativos
│       │   ├── components/          # Componentes React reutilizáveis
│       │   │   ├── ui/              # Componentes Shadcn/UI
│       │   │   ├── Layout.tsx
│       │   │   └── ProtectedRoute.tsx
│       │   ├── contexts/            # Contextos React (ex: AuthContext)
│       │   │   └── AuthContext.tsx
│       │   ├── pages/               # Páginas da aplicação
│       │   │   ├── Dashboard.tsx
│       │   │   └── Login.tsx
│       │   ├── services/            # Serviços de API
│       │   │   └── api.ts
│       │   ├── types/               # Definições de tipos TypeScript
│       │   │   └── index.ts
│       │   ├── utils/               # Utilitários e helpers
│       │   │   └── index.ts
│       │   ├── App.tsx              # Componente raiz da aplicação
│       │   └── main.tsx             # Ponto de entrada do React
│       ├── index.html
│       ├── package.json             # Dependências do Node.js
│       └── tsconfig.json            # Configurações do TypeScript
├── MANUAL_SISTEMA_LICIMAR.md      # Este manual
├── melhorias_backend.md           # Relatório de melhorias do backend
└── melhorias_frontend.md          # Relatório de melhorias do frontend
```

## 4. Orientações para Novas Funcionalidades e Melhorias

Ao adicionar novas funcionalidades ou realizar melhorias, siga estas diretrizes:

1.  **Crie um Novo Branch:** Sempre comece criando um novo branch a partir do `main` (ou `master`) para cada nova funcionalidade ou correção de bug. Use nomes descritivos (ex: `feature/nome-da-feature`, `bugfix/descricao-do-bug`).
2.  **Desenvolvimento Modular:** Mantenha o código organizado. Para o backend, crie novos blueprints para novos recursos. Para o frontend, crie novos componentes e páginas em suas respectivas pastas.
3.  **Siga as Boas Práticas:** Adote as boas práticas de desenvolvimento (validação, autenticação, tipagem, testes, etc.) mencionadas na Seção 2.
4.  **Documentação:** Documente seu código com comentários claros e atualize este manual se as alterações introduzirem novos padrões ou processos.
5.  **Testes:** Escreva testes para suas novas funcionalidades. Isso é crucial para evitar regressões e garantir a estabilidade do sistema.
6.  **Revisão de Código (Code Review):** Antes de mesclar seu branch, solicite uma revisão de código. Isso ajuda a identificar problemas, compartilhar conhecimento e garantir a qualidade.

## 5. Processo de Deploy

O deploy da aplicação envolve a configuração e execução do backend e frontend. Recomenda-se o uso de contêineres (Docker) para facilitar o deploy em diferentes ambientes.

### 5.1. Deploy do Backend (Flask)

1.  **Ambiente de Produção:** Em produção, utilize um servidor WSGI como Gunicorn ou uWSGI para servir a aplicação Flask, e um proxy reverso como Nginx para lidar com requisições HTTP e SSL.
2.  **Variáveis de Ambiente:** Configure as variáveis de ambiente (`.env`) no ambiente de deploy. Nunca comite o arquivo `.env` diretamente no repositório.
3.  **Banco de Dados:** Utilize um banco de dados robusto (PostgreSQL, MySQL) em produção. Certifique-se de que as migrações do banco de dados sejam aplicadas antes de iniciar a aplicação.
4.  **Instalação de Dependências:** Instale as dependências do `requirements.txt`.
    ```bash
pip install -r backend/licimar_mvp_app/requirements.txt
    ```
5.  **Execução (Exemplo com Gunicorn):**
    ```bash
gunicorn -w 4 -b 0.0.0.0:5000 "backend.licimar_mvp_app.src.main:create_app()"
    ```
    (Assumindo que `create_app` é importável e o diretório `backend/licimar_mvp_app/src` está no `PYTHONPATH`)

### 5.2. Deploy do Frontend (React)

1.  **Build da Aplicação:** Crie a versão de produção do frontend.
    ```bash
cd frontend/licimar_mvp_frontend
npm install
npm run build
    ```
    Isso gerará os arquivos estáticos na pasta `dist` (ou `build`).
2.  **Servidor Estático:** Sirva os arquivos estáticos gerados por um servidor web (Nginx, Apache) ou um serviço de hospedagem de sites estáticos (Netlify, Vercel).
3.  **Variáveis de Ambiente:** Certifique-se de que a variável `VITE_API_URL` no arquivo `.env` do frontend aponte para a URL do seu backend em produção.

### 5.3. Docker (Recomendado)

Crie arquivos `Dockerfile` para o backend e frontend, e um `docker-compose.yml` para orquestrar os serviços. Isso padroniza o ambiente de deploy e facilita a portabilidade.

## 6. Versionamento e Rollbacks

### 6.1. Estratégia de Versionamento (Git Flow)

Recomenda-se a adoção do Git Flow ou uma estratégia similar para gerenciar o versionamento do código. Isso envolve branches dedicados para `feature`, `develop`, `release` e `main` (ou `master`).

*   **`main` (ou `master`):** Contém o código de produção estável.
*   **`develop`:** Contém o código mais recente integrado, pronto para a próxima release.
*   **`feature/*`:** Branches para o desenvolvimento de novas funcionalidades.
*   **`release/*`:** Branches para preparar novas releases, incluindo testes finais e correções de bugs.
*   **`hotfix/*`:** Branches para correções urgentes em produção.

### 6.2. Commits Semânticos

Utilize mensagens de commit semânticas para descrever claramente o propósito de cada alteração. Exemplos:

*   `feat: Adiciona nova funcionalidade de gerenciamento de usuários`
*   `fix: Corrige bug de cálculo de estoque`
*   `docs: Atualiza manual do sistema`
*   `refactor: Refatora módulo de autenticação`
*   `style: Formata arquivos com Prettier`

### 6.3. Tags de Versão

Marque as releases de produção com tags de versão (ex: `v1.0.0`, `v1.0.1`). Isso facilita a identificação de versões específicas e o rollback.

### 6.4. Rollback

Em caso de problemas após um deploy, o Git permite reverter para uma versão anterior:

1.  **Identifique o Commit Problemático:** Use `git log` para encontrar o hash do commit que introduziu o problema.
2.  **Reverta o Commit:**
    ```bash
git revert <hash_do_commit_problematico>
    ```
    Isso cria um novo commit que desfaz as alterações do commit problemático, mantendo o histórico.
3.  **Reverta para um Estado Anterior (com cautela):** Se precisar voltar a um estado anterior específico, use `git reset --hard <hash_do_commit_anterior>`. **ATENÇÃO:** Isso reescreve o histórico e deve ser usado com extrema cautela, especialmente em branches compartilhados, pois pode causar perda de trabalho.

## 7. Orientações Iniciais para o Desenvolvimento

Para começar a trabalhar no projeto Licimar após aplicar as alterações:

### 7.1. Configuração do Backend

1.  **Navegue até o diretório do backend:**
    ```bash
cd licimar_dsv/backend/licimar_mvp_app
    ```
2.  **Crie o arquivo `.env`:** Copie o conteúdo de `.env.example` para um novo arquivo chamado `.env` e ajuste as variáveis conforme necessário (especialmente `SECRET_KEY` e `DATABASE_URL`).
    ```bash
cp .env.example .env
    ```
3.  **Crie um ambiente virtual e instale as dependências:**
    ```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
    ```
4.  **Inicialize o banco de dados:**
    ```bash
python3 init_database.py
    ```
    Este script criará o banco de dados SQLite e populará com dados iniciais (usuário admin, categorias, ambulantes, etc.).
5.  **Execute a aplicação Flask:**
    ```bash
python3 src/main.py
    ```
    A API estará disponível em `http://localhost:5000`.

### 7.2. Configuração do Frontend

1.  **Navegue até o diretório do frontend:**
    ```bash
cd licimar_dsv/frontend/licimar_mvp_frontend
    ```
2.  **Crie o arquivo `.env`:** Copie o conteúdo de `.env.example` (se houver) para um novo arquivo `.env` e defina a URL da API.
    ```bash
cp .env.example .env
    ```
    Adicione a linha:
    ```
VITE_API_URL=http://localhost:5000
    ```
3.  **Instale as dependências:**
    ```bash
npm install
    ```
4.  **Execute a aplicação React:**
    ```bash
npm run dev
    ```
    A aplicação estará disponível em `http://localhost:5173` (ou outra porta, conforme configurado pelo Vite).

### 7.3. Credenciais Iniciais

*   **Usuário Admin:**
    *   **Login:** `admin`
    *   **Senha:** `admin123`

## 8. Próximos Passos e Roadmap

Este projeto estabeleceu uma base robusta. Sugestões para próximos passos incluem:

*   **Implementação Completa do Frontend:** Finalizar todas as páginas e funcionalidades da aba "Gerenciar" no frontend (CRUDs para Produtos, Categorias, Regras de Cobrança, Usuários, Relatórios, Logs).
*   **Testes Automatizados:** Implementar testes unitários e de integração para backend e frontend.
*   **Dockerização:** Criar Dockerfiles e Docker Compose para facilitar o deploy.
*   **Otimização de Performance:** Otimizar queries de banco de dados e o carregamento de recursos no frontend.
*   **Notificações:** Adicionar sistema de notificações (ex: estoque baixo, pedidos pendentes).
*   **Internacionalização (i18n):** Suporte a múltiplos idiomas.
*   **Relatórios Avançados:** Implementar mais opções de relatórios e visualizações de dados.
*   **Melhorias de UI/UX:** Refinar a interface do usuário e a experiência do usuário com base em feedback.

Este manual será atualizado conforme o projeto evolui.
