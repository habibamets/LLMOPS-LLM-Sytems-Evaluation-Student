FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .
RUN uv sync --frozen
# Téléchargement des ressources nécessaires pour l'analyse NLP d'Evidently
RUN uv run python -m nltk.downloader words stopwords punkt_tab

COPY . .

CMD ["sh", "-c", "uv run python src/app.py && uv run python src/check_drift.py"]