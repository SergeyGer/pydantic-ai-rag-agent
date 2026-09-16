FROM python:3.14-slim

# Keep the interpreter quiet and unbuffered (important for container logs).
# Disabling bytecode writing keeps the app compatible with a read-only root FS.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source
COPY . .

# Run as an unprivileged user instead of root
RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Default to the API service (the CLI can be run with `python -m src.main`)
CMD ["python", "-m", "src.api"]
