FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .
RUN uv sync --frozen
RUN uv run python -m nltk.downloader words stopwords punkt_tab

COPY . .

# Exécution de l'Évaluateur puis du Gatekeeper
CMD ["sh", "-c", "uv run python src/app.py && uv run python src/check_structure.py"]