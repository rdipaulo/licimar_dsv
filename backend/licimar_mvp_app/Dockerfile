# Dockerfile para o Backend Flask (SQLite)

FROM python:3.10-slim

WORKDIR /app

# Copia o arquivo de requisitos e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação
COPY . .

# Expõe a porta que o Gunicorn irá escutar
EXPOSE 5000

# Comando para rodar a aplicação com Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.main:create_app()"]
