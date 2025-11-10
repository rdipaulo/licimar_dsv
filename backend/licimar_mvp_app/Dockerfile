# Dockerfile para o Backend Flask com SQL Server

# Usa uma imagem base mais completa para instalar o driver ODBC
FROM python:3.10-slim-buster

# Instala o driver ODBC 17 para SQL Server
# Isso é necessário para que o pyodbc funcione
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gnupg \
    curl \
    build-essential \
    unixodbc-dev \
    # Instala o driver ODBC da Microsoft
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    # Instala o driver para o pyodbc
    && apt-get install -y locales \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de requisitos e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação
COPY . .

# Expõe a porta que o Gunicorn irá escutar
EXPOSE 5000

# Comando para rodar a aplicação com Gunicorn
# O Gunicorn é um servidor WSGI robusto para produção
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.main:create_app()"]
