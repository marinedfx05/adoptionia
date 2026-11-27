# 1. Partir d'une image officielle qui contient déjà Python 3.11 (version allégée)
FROM python:3.11-slim

# 2. Travailler dans le dossier /app à l'intérieur de la boîte
WORKDIR /app

# 3. Installer les bibliothèques du projet
#    (AVANT de copier le code : Docker réutilise cette étape tant que requirements.txt ne change pas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copier le code du projet dans la boîte
COPY . .