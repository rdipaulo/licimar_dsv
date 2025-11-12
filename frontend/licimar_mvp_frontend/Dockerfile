# Dockerfile para o Frontend React (Vite)

# Fase de Build
FROM node:18-alpine as build

WORKDIR /app

# Copia package.json e package-lock.json (ou yarn.lock/pnpm-lock.yaml)
COPY package*.json ./

# Instala dependências
RUN npm install

# Copia o restante do código
COPY . .

# Cria o build de produção
RUN npm run build

# Fase de Produção (Servidor Nginx)
FROM nginx:stable-alpine as production

# Copia o build do React para o diretório de serviço do Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copia a configuração customizada do Nginx (se houver)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expõe a porta 80 (padrão do Nginx)
EXPOSE 80

# Comando para iniciar o Nginx
CMD ["nginx", "-g", "daemon off;"]
