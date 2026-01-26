FROM node:18-alpine

WORKDIR /app

# Copier les fichiers de configuration
COPY package.json ./
COPY package-lock.json* ./

# Installer les dépendances
RUN npm install

# Copier le reste du code
COPY public ./public
COPY src ./src

# Exposer le port
EXPOSE 3000

# Commande de démarrage
CMD ["npm", "start"]
