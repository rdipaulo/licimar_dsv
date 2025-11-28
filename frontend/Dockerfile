FROM node:20-alpine

WORKDIR /app

# Copiar package files
COPY frontend/licimar_mvp_frontend/package.json ./
COPY frontend/licimar_mvp_frontend/package-lock.json* ./
COPY frontend/licimar_mvp_frontend/pnpm-lock.yaml* ./

# Instalar dependências
RUN npm install --legacy-peer-deps

# Copiar código
COPY frontend/licimar_mvp_frontend/ ./

# Build
RUN npm run build

# Usar nginx para servir
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
