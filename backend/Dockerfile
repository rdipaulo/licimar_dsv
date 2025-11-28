FROM python:3.13-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libcairo2-dev \
    libpango-1.0-0 \
    libpango-cairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY backend/licimar_mvp_app/requirements.txt ./requirements.txt

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar WeasyPrint para PDFs
RUN pip install --no-cache-dir weasyprint

# Copiar código backend
COPY backend/licimar_mvp_app/ ./backend/

# Criar diretório de instância
RUN mkdir -p ./backend/instance

# Variáveis de ambiente
ENV FLASK_APP=backend/app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite:///./backend/instance/licimar.db
ENV SECRET_KEY=your-secret-key-change-this

WORKDIR /app/backend

# Executar migrations e setup
RUN python -c "from src.main import create_app; from src.database import db; app = create_app(); app.app_context().push(); db.create_all(); print('✓ Database initialized')"

# Exposer porta
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/auth/login', timeout=2)" || exit 1

# Comando para iniciar
CMD ["python", "app.py"]
