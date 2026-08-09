FROM python:3.12-slim

# Prevent Python from buffering outputs (ensures instant logs)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy the pre-compiled uv binary directly (faster than pip install uv)
COPY --from=ghcr.io/astral-sh/uv:0.11.32 /uv /uvx /bin/

# Copy dependency definition files first (for layer caching)
COPY pyproject.toml uv.lock ./

# Install dependencies into .venv
RUN uv sync --frozen

# Copy source code and raw data assets
COPY src ./src
COPY data/raw ./data/raw

# Create a non-root user
RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app

# Switch to the non-root user for all subsequent commands and runtime
USER appuser

EXPOSE 7860

# Launch the app using uv run to leverage the virtualenv automatically
CMD ["uv", "run", "python", "-m", "src.app.gradio_app"]
