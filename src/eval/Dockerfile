FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

WORKDIR /app

COPY pyproject.toml uv.lock .
RUN uv sync --frozen
RUN uv run python -m nltk.downloader words stopwords punkt_tab

COPY . .

CMD ["sh", "-c", "uv run python eval_rag.py && uv run python check_semantic.py"]