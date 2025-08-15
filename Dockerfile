# Install uv
FROM astral/uv:python3.12-bookworm-slim

# Change the working directory to the `app` directory
WORKDIR /app

# Copy the lockfile and `pyproject.toml` into the image
COPY uv.lock /app/uv.lock
COPY pyproject.toml /app/pyproject.toml

# Install dependencies
RUN uv sync --frozen --no-install-project

# Copy the project into the image
COPY src /app/src

# Sync the project
RUN uv sync --frozen

CMD ["uv", "run", "fastapi", "run", "src/main.py"]
