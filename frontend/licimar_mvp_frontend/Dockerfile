# Dockerfile para o Frontend React (Vite)

# Fase de Build
FROM node:18-alpine as build

WORKDIR /app

# Copia package.json e package-lock.json (ou yarn.lock/pnpm-lock.yaml)
COPY package*.json ./

# Instala dependências, usando --legacy-peer-deps para resolver conflitos
# O problema de dependência do frontend é resolvido aqui
RUN npm install --legacy-peer-deps

# Copia o restante do código
COPY . .

# Cria o build de produção
RUN npm run build

# Fase de Produção (Servidor Nginx)
FROM nginx:stable-alpine as production

# Copia o build do React para o diretório de serviço do Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Expõe a porta 80 (padrão do Nginx)
EXPOSE 80

# Comando para iniciar o Nginx
CMD ["nginx", "-g", "daemon off;"]
