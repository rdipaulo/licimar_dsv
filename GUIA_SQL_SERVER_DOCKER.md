# Guia Completo: SQL Server no Docker com SSMS para Windows

## Introdução

Este guia fornece instruções passo a passo para configurar o **SQL Server 2022** em um contêiner Docker no Windows, permitindo que você use o **SQL Server Management Studio (SSMS)** para gerenciar o banco de dados da aplicação Licimar com persistência de dados.

## Pré-requisitos

*   **Docker Desktop instalado** no Windows (versão mais recente recomendada).
*   **SQL Server Management Studio (SSMS)** instalado (download gratuito em [https://learn.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms](https://learn.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms)).
*   **Git** instalado.
*   **Python 3.9+** e **Node.js 18+** instalados (para desenvolvimento local, se necessário).

## Parte 1: Configuração do Docker Desktop para SQL Server

### Passo 1.1: Verificar Recursos do Sistema

O SQL Server no Docker requer recursos significativos. Certifique-se de que seu notebook tem:

*   **Mínimo 4GB de RAM** (recomendado 8GB ou mais).
*   **Pelo menos 10GB de espaço em disco** disponível.

### Passo 1.2: Configurar Docker Desktop para Windows

1.  **Abra o Docker Desktop**.
2.  **Acesse as configurações** (ícone de engrenagem no canto superior direito).
3.  **Navegue para "Resources"** (Recursos).
4.  **Configure a memória:**
    *   Defina **Memory** para pelo menos **4GB** (recomendado **6-8GB**).
    *   Defina **CPUs** para pelo menos **2** (recomendado **4**).
5.  **Clique em "Apply & Restart"** para aplicar as mudanças.

## Parte 2: Iniciando o SQL Server no Docker

### Passo 2.1: Subir o SQL Server

Você tem duas opções:

#### Opção A: Usar o `docker-compose.yml` (Recomendado)

Este é o método mais simples, pois orquestra o SQL Server, o backend Flask e o frontend React.

1.  **Navegue até a raiz do seu projeto** (onde está o `docker-compose.yml`):
    ```bash
cd caminho/para/licimar_dsv
    ```
2.  **Suba os contêineres:**
    ```bash
docker-compose up --build -d
    ```
    *   O comando `--build` constrói as imagens.
    *   O comando `-d` executa em segundo plano.
3.  **Aguarde cerca de 30-60 segundos** para o SQL Server inicializar completamente.
4.  **Verifique o status:**
    ```bash
docker-compose ps
    ```
    Você deve ver os três serviços (`db`, `backend`, `frontend`) com status `Up`.

#### Opção B: Usar um Comando Docker Direto (Se preferir apenas o SQL Server)

```bash
docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=LicimarPassword123!" -p 1433:1433 --name licimar_sqlserver -d mcr.microsoft.com/mssql/server:2022-latest
```

### Passo 2.2: Verificar se o SQL Server está Rodando

1.  **Abra o PowerShell ou Command Prompt**.
2.  **Execute:**
    ```bash
docker ps
    ```
    Você deve ver um contêiner com a imagem `mssql/server:2022-latest` com status `Up`.

## Parte 3: Conectar ao SQL Server com SSMS

### Passo 3.1: Abrir SQL Server Management Studio

1.  **Abra o SSMS** (procure por "SQL Server Management Studio" no menu Iniciar).

### Passo 3.2: Conectar ao Servidor

1.  **Na janela "Connect to Server"**, preencha os seguintes dados:
    *   **Server name:** `localhost,1433` (ou `127.0.0.1,1433`)
    *   **Authentication:** Selecione **"SQL Server Authentication"**
    *   **Login:** `sa`
    *   **Password:** `LicimarPassword123!`
2.  **Clique em "Connect"**.

Se a conexão for bem-sucedida, você verá o Object Explorer com o servidor conectado.

### Passo 3.3: Criar o Banco de Dados Licimar (Se necessário)

Se o banco de dados não foi criado automaticamente pelo script `init_database.py`, você pode criá-lo manualmente:

1.  **No Object Explorer**, clique com o botão direito em **"Databases"** e selecione **"New Database"**.
2.  **Na janela "New Database"**, preencha:
    *   **Database name:** `licimar_db`
3.  **Clique em "OK"**.

## Parte 4: Inicializar o Banco de Dados com Dados Iniciais

### Passo 4.1: Executar o Script de Inicialização

Se você usou o `docker-compose.yml`, o script `init_database.py` é executado automaticamente. Caso contrário, execute manualmente:

1.  **Abra o PowerShell ou Command Prompt**.
2.  **Navegue até o diretório do backend:**
    ```bash
cd licimar_dsv\backend\licimar_mvp_app
    ```
3.  **Execute o script:**
    ```bash
python3 init_database.py
    ```
    Este script criará as tabelas e populará o banco com dados iniciais (usuário admin, categorias, ambulantes, etc.).

### Passo 4.2: Verificar as Tabelas no SSMS

1.  **No SSMS**, navegue até **Databases** > **licimar_db** > **Tables**.
2.  Você deve ver as seguintes tabelas:
    *   `ambulantes`
    *   `categorias`
    *   `logs`
    *   `pedidos`
    *   `produtos`
    *   `regras_cobranca`
    *   `usuarios`

## Parte 5: Parar e Reiniciar o SQL Server

### Passo 5.1: Parar o SQL Server

Se você usou o `docker-compose.yml`:

```bash
docker-compose down
```

Se você usou um comando Docker direto:

```bash
docker stop licimar_sqlserver
```

### Passo 5.2: Reiniciar o SQL Server

Se você usou o `docker-compose.yml`:

```bash
docker-compose up -d
```

Se você usou um comando Docker direto:

```bash
docker start licimar_sqlserver
```

**Importante:** Os dados persistem no volume Docker, então você não perderá nenhuma informação ao parar e reiniciar o contêiner.

## Parte 6: Troubleshooting

### Problema: "Login failed for user 'sa'"

**Solução:**
*   Verifique se a senha está correta: `LicimarPassword123!`
*   Aguarde alguns segundos após iniciar o contêiner antes de tentar conectar.
*   Reinicie o contêiner: `docker-compose restart db`

### Problema: "Connection timeout"

**Solução:**
*   Verifique se o Docker Desktop está rodando.
*   Verifique se o contêiner está rodando: `docker ps`
*   Verifique se a porta 1433 não está sendo usada por outro serviço.

### Problema: "Insufficient memory"

**Solução:**
*   Aumente a memória alocada ao Docker Desktop (conforme Passo 1.2).
*   Feche outros aplicativos que consomem muita memória.

### Problema: "Database 'licimar_db' does not exist"

**Solução:**
*   Execute o script `init_database.py` novamente.
*   Ou crie o banco manualmente via SSMS (conforme Passo 3.3).

## Parte 7: Backup e Restore do Banco de Dados

### Passo 7.1: Fazer Backup via SSMS

1.  **No SSMS**, clique com o botão direito no banco de dados **licimar_db**.
2.  Selecione **Tasks** > **Back Up**.
3.  **Configure o local do backup** e clique em **OK**.

### Passo 7.2: Restaurar Backup via SSMS

1.  **No SSMS**, clique com o botão direito em **Databases**.
2.  Selecione **Restore Database**.
3.  **Selecione o arquivo de backup** e clique em **OK**.

## Parte 8: Próximos Passos

Agora que o SQL Server está configurado e rodando:

1.  **Configure o backend Flask** conforme as instruções no `MANUAL_SISTEMA_LICIMAR.md`.
2.  **Configure o frontend React** conforme as instruções no `MANUAL_SISTEMA_LICIMAR.md`.
3.  **Acesse a aplicação** em `http://localhost:3000` (ou `http://localhost:5173` se estiver usando o Vite em desenvolvimento).
4.  **Faça login** com as credenciais iniciais:
    *   **Usuário:** `admin`
    *   **Senha:** `admin123`

## Referências

*   [Documentação oficial do SQL Server no Docker](https://learn.microsoft.com/en-us/sql/linux/quickstart-install-connect-docker)
*   [SQL Server Management Studio Download](https://learn.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms)
*   [Docker Documentation](https://docs.docker.com/)

---

**Autor:** Manus AI  
**Data:** Novembro de 2025  
**Versão:** 1.0
