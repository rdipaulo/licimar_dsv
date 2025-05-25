# Guia de Hospedagem Gratuita para o Sistema Licimar

Este guia apresenta as melhores opções de hospedagem gratuita para o sistema Licimar, detalhando o processo de implantação tanto para o backend (Flask/Python) quanto para o frontend (React).

## Opções de Hospedagem Gratuita

### 1. Render (Recomendado)

**Vantagens:**
- Suporta tanto aplicações Python (backend) quanto estáticas (frontend)
- Fácil integração com GitHub
- Interface amigável
- Banco de dados SQLite pode ser hospedado junto com a aplicação
- Oferece HTTPS gratuito

**Limitações:**
- Aplicações gratuitas hibernam após 15 minutos de inatividade
- 512 MB de RAM na versão gratuita
- Limite de 750 horas de uso por mês

**Processo de Implantação:**

1. **Backend (Flask):**
   - Crie uma conta em [render.com](https://render.com)
   - Clique em "New" e selecione "Web Service"
   - Conecte seu repositório GitHub
   - Configure:
     - Nome: `licimar-backend`
     - Runtime: `Python 3`
     - Build Command: `pip install -r backend/licimar_mvp_app/requirements.txt`
     - Start Command: `cd backend/licimar_mvp_app && python src/main.py`
     - Selecione o plano gratuito

2. **Frontend (React):**
   - Clique em "New" e selecione "Static Site"
   - Conecte seu repositório GitHub
   - Configure:
     - Nome: `licimar-frontend`
     - Build Command: `cd frontend/licimar_mvp_frontend && npm install && npm run build`
     - Publish Directory: `frontend/licimar_mvp_frontend/dist`
     - Selecione o plano gratuito

### 2. Railway

**Vantagens:**
- Suporte a Python e Node.js
- Implantação simples via GitHub
- Oferece bancos de dados PostgreSQL gratuitos
- Bom desempenho

**Limitações:**
- Créditos limitados na versão gratuita ($5/mês)
- Após os créditos, é necessário upgrade

**Processo de Implantação:**

1. **Backend (Flask):**
   - Crie uma conta em [railway.app](https://railway.app)
   - Clique em "New Project" e selecione "Deploy from GitHub repo"
   - Selecione seu repositório
   - Configure as variáveis de ambiente necessárias
   - Railway detectará automaticamente que é uma aplicação Python

2. **Frontend (React):**
   - Crie um novo projeto
   - Selecione seu repositório
   - Configure:
     - Build Command: `cd frontend/licimar_mvp_frontend && npm install && npm run build`
     - Start Command: `cd frontend/licimar_mvp_frontend && npx serve -s dist`

### 3. Vercel + PythonAnywhere

**Combinação para separar frontend e backend:**

**Vercel (Frontend):**
- Otimizado para aplicações React
- Implantação contínua via GitHub
- Excelente desempenho
- HTTPS gratuito

**PythonAnywhere (Backend):**
- Especializado em aplicações Python
- Suporte a Flask
- Banco de dados SQLite incluído
- Não hiberna como outros serviços gratuitos

**Processo de Implantação:**

1. **Backend (PythonAnywhere):**
   - Crie uma conta em [pythonanywhere.com](https://www.pythonanywhere.com)
   - Vá para "Web" e clique em "Add a new web app"
   - Selecione "Flask" e Python 3.9
   - Configure o caminho para o arquivo WSGI
   - Faça upload dos arquivos do backend via "Files"
   - Instale as dependências usando o console

2. **Frontend (Vercel):**
   - Crie uma conta em [vercel.com](https://vercel.com)
   - Importe seu repositório GitHub
   - Configure:
     - Framework Preset: Vite
     - Root Directory: `frontend/licimar_mvp_frontend`
     - Build Command: `npm run build`
     - Output Directory: `dist`

## Preparação para Implantação

### Ajustes no Backend

1. **Crie um arquivo `wsgi.py` na raiz do backend:**

```python
from src.main import app as application

if __name__ == "__main__":
    application.run()
```

2. **Adicione um arquivo `Procfile` para serviços como Render:**

```
web: gunicorn wsgi:application
```

3. **Atualize o `requirements.txt` para incluir gunicorn:**

```
Flask==3.1.0
Flask-SQLAlchemy==3.1.1
PyJWT==2.10.1
PyMySQL==1.1.1
SQLAlchemy==2.0.40
cryptography==36.0.2
gunicorn==21.2.0
```

4. **Configure CORS para permitir requisições do frontend:**

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

### Ajustes no Frontend

1. **Crie um arquivo `.env.production` para configurar a URL da API:**

```
VITE_API_URL=https://sua-api-backend.onrender.com
```

2. **Atualize o arquivo de API para usar a variável de ambiente:**

```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export const fetchData = async (endpoint) => {
  const response = await fetch(`${API_URL}${endpoint}`);
  return response.json();
};
```

## Implantação Passo a Passo no Render (Recomendado)

### Backend

1. Crie uma conta no Render e faça login
2. Clique em "New" e selecione "Web Service"
3. Conecte seu repositório GitHub ou faça upload do código
4. Configure o serviço:
   - Nome: `licimar-backend`
   - Runtime: `Python 3`
   - Build Command: `pip install -r backend/licimar_mvp_app/requirements.txt`
   - Start Command: `cd backend/licimar_mvp_app && gunicorn --chdir src main:app`
   - Selecione o plano gratuito
5. Clique em "Create Web Service"
6. Aguarde a implantação (pode levar alguns minutos)
7. Anote a URL gerada (será algo como `https://licimar-backend.onrender.com`)

### Frontend

1. No Render, clique em "New" e selecione "Static Site"
2. Conecte seu repositório GitHub ou faça upload do código
3. Configure o site:
   - Nome: `licimar-frontend`
   - Build Command: `cd frontend/licimar_mvp_frontend && npm install && npm run build`
   - Publish Directory: `frontend/licimar_mvp_frontend/dist`
   - Variáveis de ambiente: Adicione `VITE_API_URL` com o valor da URL do backend
   - Selecione o plano gratuito
4. Clique em "Create Static Site"
5. Aguarde a implantação
6. Acesse a URL gerada (será algo como `https://licimar-frontend.onrender.com`)

## Considerações Finais

- **Backup de Dados**: Como o SQLite está sendo usado, faça backups regulares do arquivo de banco de dados
- **Monitoramento**: Verifique regularmente se o serviço está ativo, especialmente após períodos de inatividade
- **Escalabilidade**: Se o uso crescer além dos limites gratuitos, considere migrar para um plano pago ou para outra solução como AWS ou DigitalOcean

Para qualquer dúvida ou problema durante a implantação, consulte a documentação oficial do serviço escolhido ou entre em contato para suporte adicional.
