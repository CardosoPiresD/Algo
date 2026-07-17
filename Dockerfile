FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY hermes/ hermes/

# Par défaut: un cycle de rebalancing paper en dry-run (sécurité).
# Pour exécuter réellement: docker run ... python -m hermes.main paper
CMD ["python", "-m", "hermes.main", "paper", "--dry-run"]
