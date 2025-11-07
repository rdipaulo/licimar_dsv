# Dockerfile para o Backend Flask

# Usa a imagem oficial do Python como base
FROM python:3.10-slim

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
