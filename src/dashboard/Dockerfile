FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

WORKDIR /app

COPY src/dashboard/pyproject.toml .
COPY src/dashboard/uv.lock .
RUN uv sync --frozen

COPY src/dashboard/dashboard_push.py .

CMD ["uv", "run", "python", "dashboard_push.py"]