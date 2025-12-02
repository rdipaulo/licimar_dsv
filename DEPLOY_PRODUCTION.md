# Guia de Deploy em Produção - Licimar MVP

## Pré-requisitos

- Python 3.9+
- PostgreSQL 12+ (recomendado para produção) ou MySQL 5.7+
- Git
- pip

## Instalação em Servidor de Produção

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/licimar_dsv.git
cd licimar_dsv/backend/licimar_mvp_app
```

### 2. Criar ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env com suas configurações
nano .env  # ou use seu editor favorito
```

**Configurações críticas para produção:**

- `SECRET_KEY`: Gerar uma chave forte
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

- `DATABASE_URL`: Configurar com banco de dados de produção
  ```
  # PostgreSQL
  DATABASE_URL=postgresql://user:password@db.example.com:5432/licimar

  # MySQL
  DATABASE_URL=mysql+pymysql://user:password@db.example.com:3306/licimar
  ```

- `CORS_ORIGINS`: Adicionar seu domínio
  ```
  CORS_ORIGINS=https://seu-dominio.com,https://www.seu-dominio.com
  ```

- `FLASK_ENV`: Sempre `production`
  ```
  FLASK_ENV=production
  ```

### 5. Inicializar banco de dados

```bash
# Executar migrações (se usar Alembic)
# flask db upgrade

# Ou criar tabelas
python -c "
from src.main import create_app
from src.database import db
app = create_app('production')
with app.app_context():
    db.create_all()
    print('[OK] Banco de dados inicializado')
"
```

### 6. Executar aplicação com Gunicorn

```bash
# Modo simples
gunicorn --workers 4 --bind 0.0.0.0:8000 app:app

# Com arquivo de configuração (recomendado)
gunicorn --config gunicorn_config.py app:app
```

**Arquivo gunicorn_config.py:**
```python
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
timeout = 30
keepalive = 2
accesslog = "-"
errorlog = "-"
loglevel = "info"
```

### 7. Configurar Nginx como Reverse Proxy

```nginx
upstream licimar_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;

    # Redirecionar HTTP para HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seu-dominio.com www.seu-dominio.com;

    # Certificados SSL (usar Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;

    # Melhorias de segurança
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Headers de segurança
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;

    location / {
        proxy_pass http://licimar_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Servir arquivos estáticos
    location /static/ {
        alias /path/to/licimar_mvp_app/static/;
        expires 7d;
    }
}
```

### 8. Configurar Supervisor para gerenciar o processo

```ini
# /etc/supervisor/conf.d/licimar.conf

[program:licimar]
command=/home/user/licimar_dsv/backend/licimar_mvp_app/venv/bin/gunicorn --config gunicorn_config.py app:app
directory=/home/user/licimar_dsv/backend/licimar_mvp_app
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/licimar/gunicorn.log

[group:licimar]
programs=licimar
```

### 9. Instalar e configurar SSL (Let's Encrypt)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Gerar certificado
sudo certbot certonly --nginx -d seu-dominio.com -d www.seu-dominio.com

# Renovação automática
sudo systemctl enable certbot.timer
```

### 10. Monitoramento e Logs

```bash
# Ver logs em tempo real
tail -f /var/log/licimar/gunicorn.log

# Rotação de logs
# Usar logrotate para rotacionar logs automaticamente
```

## Checklist de Deploy

- [ ] DATABASE_URL configurado com banco de produção
- [ ] SECRET_KEY alterado para valor seguro
- [ ] CORS_ORIGINS configurado com seu domínio
- [ ] FLASK_ENV = production
- [ ] SSL/TLS configurado (HTTPS)
- [ ] Backup do banco de dados configurado
- [ ] Monitoramento e alertas configurados
- [ ] Firewall configurado para liberar apenas portas 80/443
- [ ] Testes de funcionalidade realizados
- [ ] Documentação atualizada para sua infraestrutura

## Solução de Problemas

### Erro: "No module named 'weasyprint'"
```bash
pip install WeasyPrint==61.0
```

### Erro: "Could not import app"
```bash
# Certifique-se de estar no diretório correto
cd /path/to/licimar_mvp_app

# Verificar se app.py existe
ls -la app.py
```

### Erro: "Connection refused" ao banco de dados
```bash
# Verificar se DATABASE_URL está correto
# Verificar se banco de dados está rodando
# Verificar firewall e permissões de rede
```

## Recursos Adicionais

- [Documentação Gunicorn](https://docs.gunicorn.org/)
- [Documentação Nginx](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Supervisor](http://supervisord.org/)

## Suporte

Para problemas ou dúvidas, abra uma issue no repositório do projeto.
