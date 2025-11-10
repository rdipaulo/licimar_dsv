# Manual de Desenvolvimento e Operação Sênior - Projeto Licimar

## Introdução

Este manual é o produto final de uma revisão sênior de QA e Desenvolvimento, garantindo que o projeto Licimar seja robusto, seguro e pronto para produção. Ele aborda a configuração do ambiente, a execução via Docker com SQL Server, as boas práticas de desenvolvimento e as diretrizes de segurança para um deploy online.

**Foco:** **SQL Server no Docker** e **Instruções Sequenciais Claras**.

## Parte 1: Configuração Inicial e Aplicação das Alterações

### Passo 1.1: Pré-requisitos (Checklist)

Certifique-se de que todos os itens abaixo estão instalados e configurados:

| Item | Versão Recomendada | Status |
| :--- | :--- | :--- |
| **Git** | Mais recente | OK |
| **Python** | 3.10+ | OK |
| **Node.js** | 18+ | OK |
| **Docker Desktop** | Mais recente (Windows) | OK |
| **SQL Server Management Studio (SSMS)** | Mais recente | OK |

### Passo 1.2: Obtenção e Estrutura do Código

1.  **Descompacte o arquivo `licimar_dsv.zip`** em um diretório de sua preferência (Ex: `C:\Projetos\licimar_dsv`).
2.  **Navegue até o diretório raiz** do projeto no terminal (PowerShell ou CMD):
    ```powershell
    cd C:\Projetos\licimar_dsv
    ```
3.  **Estrutura Simplificada:** O projeto agora tem uma estrutura mais limpa para o Docker:
    ```
    licimar_dsv/
    ├── backend/
    │   └── licimar_mvp_app/  # Contém o código Flask, Dockerfile, requirements.txt
    ├── frontend/
    │   └── licimar_mvp_frontend/ # Contém o código React, Dockerfile, package.json
    ├── docker-compose.yml    # Orquestração (DB, Backend, Frontend)
    ├── GUIA_SQL_SERVER_DOCKER.md # Guia de conexão SSMS
    └── MANUAL_SISTEMA_LICIMAR.md # Este manual
    ```

### Passo 1.3: Aplicação das Alterações no Seu Repositório (Pull Request)

1.  **Clone seu repositório original** (se ainda não o fez):
    ```bash
    git clone https://github.com/rdipaulo/licimar_dsv.git
    cd licimar_dsv
    ```
2.  **Crie um novo branch** para as alterações:
    ```bash
    git checkout -b feature/refatoracao-senior
    ```
3.  **Copie os arquivos corrigidos:**
    *   Copie o conteúdo da pasta `backend/licimar_mvp_app/` (do projeto descompactado) para a pasta `backend/licimar_mvp_app/` do seu repositório clonado.
    *   Copie o conteúdo da pasta `frontend/licimar_mvp_frontend/` (do projeto descompactado) para a pasta `frontend/licimar_mvp_frontend/` do seu repositório clonado.
    *   Copie os arquivos `docker-compose.yml`, `GUIA_SQL_SERVER_DOCKER.md` e `MANUAL_SISTEMA_LICIMAR.md` para a raiz do seu repositório clonado.
4.  **Commit e Push:**
    ```bash
    git add .
    git commit -m "feat(senior): Reestruturação completa, SQL Server no Docker e segurança para deploy online"
    git push -u origin feature/refatoracao-senior
    ```
5.  **Abra o Pull Request** no GitHub.

## Parte 2: Execução Perfeita com SQL Server no Docker

Esta é a forma **recomendada** de rodar o projeto, garantindo ambiente isolado e persistência de dados.

### Passo 2.1: Configuração do Docker Desktop (Windows)

1.  **Abra o Docker Desktop** e certifique-se de que ele está rodando.
2.  **Verifique a alocação de recursos** (Settings -> Resources). O SQL Server exige pelo menos **4GB de RAM** e **2 CPUs** alocadas ao Docker.

### Passo 2.2: Inicialização dos Contêineres

1.  **Navegue até a raiz do projeto** (`C:\Projetos\licimar_dsv`).
2.  **Execute o comando de inicialização:**
    ```powershell
    docker-compose up --build -d
    ```
    *   `--build`: Garante que as imagens sejam construídas com as últimas correções (incluindo o driver ODBC e a correção do `npm install`).
    *   `-d`: Executa em segundo plano.

### Passo 2.3: Verificação e Validação do Status (Crucial)

1.  **Verifique o status dos serviços:**
    ```powershell
    docker-compose ps
    ```
2.  **Aguarde o Status `Up (healthy)`:**
    *   **IMPORTANTE:** O serviço `db` (SQL Server) leva tempo para inicializar. Você deve esperar até que o status de todos os serviços seja `Up` e o `db` esteja como **`(healthy)`**.
    *   Se o `db` estiver como `(unhealthy)`, aguarde mais um pouco. O `backend` só iniciará o Flask e o banco de dados após o `db` estar saudável.

### Passo 2.4: Acesso à Aplicação

Após a verificação do status:

1.  **Frontend (Aplicação Web):** Acesse `http://localhost:3000`
2.  **Backend (API):** Acesse `http://localhost:5000`
3.  **Credenciais Iniciais:**
    *   **Usuário:** `admin`
    *   **Senha:** `admin123`

### Passo 2.5: Conexão com SQL Server Management Studio (SSMS)

1.  **Abra o SSMS.**
2.  **Conecte ao Servidor:**
    *   **Server name:** `localhost,1433`
    *   **Authentication:** SQL Server Authentication
    *   **Login:** `sa`
    *   **Password:** `LicimarPassword123!`
3.  **Verifique o Banco de Dados:** O banco `licimar_db` e as tabelas (ambulantes, produtos, etc.) devem estar criados e populados.

## Parte 3: Segurança e Boas Práticas para Deploy Online

O projeto agora está estruturado para ser protegido ao ser colocado em um servidor online.

### Passo 3.1: Segurança de Ambiente (Variáveis de Ambiente)

*   **Nunca use senhas e chaves secretas diretamente no código.**
*   **Em Produção:** Use um gerenciador de segredos (ex: AWS Secrets Manager, Azure Key Vault) ou configure as variáveis de ambiente diretamente no seu servidor/plataforma de deploy.

| Variável | Uso | Valor em Produção |
| :--- | :--- | :--- |
| `SECRET_KEY` | Chave secreta do Flask (JWT, Sessão) | String aleatória e complexa (MUITO LONGA) |
| `SA_PASSWORD` | Senha do usuário `sa` do SQL Server | Senha forte e única |
| `DATABASE_URL` | String de conexão do banco de dados | Aponta para o IP/Host do seu servidor de banco de dados |
| `FLASK_ENV` | Ambiente de execução | `production` |
| `CORS_ORIGINS` | Domínios permitidos | `https://seu-dominio.com` |

### Passo 3.2: Proteção de API (CORS e HTTPS)

*   **CORS:** O backend está configurado para usar `CORS_ORIGINS` (no `.env`) para permitir acesso apenas do seu frontend. **Em produção, altere `CORS_ORIGINS` para o domínio real do seu frontend.**
*   **HTTPS:** **Obrigatório para Deploy Online.** Use um proxy reverso (Nginx ou Apache) no seu servidor para forçar o tráfego HTTPS e obter um certificado SSL (ex: Let's Encrypt).

### Passo 3.3: Logging e Monitoramento

*   O sistema está configurado para registrar logs importantes (`LOG_FILE` no `.env`).
*   **Em Produção:** Configure um sistema de monitoramento centralizado (ex: ELK Stack, Prometheus/Grafana) para coletar e analisar os logs dos contêineres.

## Parte 4: Diretrizes de Desenvolvimento Sênior

### Passo 4.1: Estratégia de Versionamento (Git Flow)

*   **`main`:** Apenas código de produção estável.
*   **`develop`:** Branch principal para integração de novas funcionalidades.
*   **`feature/*`:** Branches para novas funcionalidades (sempre a partir de `develop`).
*   **`hotfix/*`:** Correções urgentes em produção (a partir de `main`).

### Passo 4.2: Padrões de Código

*   **Backend (Python):** Siga o padrão **PEP 8** (formatação) e use **Type Hinting** (tipagem).
*   **Frontend (React/TS):** Siga o padrão **ESLint** e **Prettier** para formatação e use **TypeScript** para tipagem rigorosa.

### Passo 4.3: Testes Automatizados (Próximo Passo Crítico)

*   **Backend:** Use `pytest` para testes unitários e de integração dos endpoints da API.
*   **Frontend:** Use `Jest` ou `Vitest` para testes unitários de componentes e `Cypress` ou `Playwright` para testes E2E (End-to-End).

## Parte 5: Próximos Passos e Roadmap

1.  **Finalizar o Frontend:** Implementar todas as telas de CRUD (Create, Read, Update, Delete) para as entidades (Ambulantes, Produtos, Usuários, etc.).
2.  **Implementar Testes:** Adicionar a suíte de testes automatizados.
3.  **Configurar CI/CD:** Automatizar o processo de build, teste e deploy (ex: GitHub Actions, GitLab CI).
4.  **Otimização de Performance:** Otimizar queries e caching.

---

**Autor:** Manus AI (Equipe Sênior de Desenvolvimento)  
**Data:** Novembro de 2025  
**Versão:** 2.0 (Revisão Sênior)
