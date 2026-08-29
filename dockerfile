# =============================================================================
# Builder stage
# Installs dependencies, copies source + tests + raw knowledge base, and
# runs the smoke test (which produces the vector store artifact)
# =============================================================================
FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Pre-compiled uv binary (faster than pip install uv). Only needed here —
COPY --from=ghcr.io/astral-sh/uv:0.11.32 /uv /uvx /bin/

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# --no-dev excludes the dev dependency group from the environment
RUN uv sync --frozen --no-dev

COPY src ./src
COPY tests ./tests
COPY data/raw ./data/raw

# Running the smoke test also builds the vector store: ensure_vector_store()
# NOTE: need to use docker secrets to pass key during image build process
RUN --mount=type=secret,id=openai_api_key \
    OPENAI_API_KEY=$(cat /run/secrets/openai_api_key) \
    uv run --no-dev python -m tests.smoke_test


# =============================================================================
# Final stage
# Fresh base image containing only the built virtual environment, app code,
# and the pre-built vector store. No uv binary, no raw knowledge base, no
# test files, no dev dependencies — keeps the shipped image minimal and
# avoids baking raw source documents into the deployed artifact.
# =============================================================================
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN useradd --create-home appuser

COPY --from=builder --chown=appuser:appuser /app/.venv ./.venv
COPY --from=builder --chown=appuser:appuser /app/src ./src
COPY --from=builder --chown=appuser:appuser /app/data/vector_db ./data/vector_db

# Puts the venv's python/uv on PATH; required since uv is not included
# in the final stage
ENV PATH="/app/.venv/bin:$PATH"

USER appuser

EXPOSE 7860

# --no-dev avoids uv's implicit sync-on-mismatch reinstalling dev dependencies
# CMD ["uv", "run", "--no-dev", "python", "-m", "src.app.gradio_app"]
CMD ["python", "-m", "src.app.gradio_app"]