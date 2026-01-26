FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY app.py .
COPY .env* .

# Créer des répertoires pour les volumes
RUN mkdir -p /app/output/model /app/Data

# Exposer le port
EXPOSE 5000

# Commande de démarrage
CMD ["python", "app.py"]
