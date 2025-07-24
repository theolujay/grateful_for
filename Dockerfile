# ---- Builder Stage: Installs dependencies ----
FROM python:3.13-slim-bookworm AS builder

# Install build-time system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Set up virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --retries 3 --timeout 60 -r requirements.txt


# ---- Final Stage: The actual application image ----
FROM python:3.13-slim-bookworm

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Create a non-root user and group
RUN addgroup --system app && adduser --system --group app

# Copy virtual environment from the builder stage
COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV

# Set working directory
WORKDIR /home/app/web

# Copy application code as the non-root user
COPY --chown=app:app . .

# Copy and set up entrypoint script
COPY --chown=app:app entrypoint.sh .
RUN chmod +x entrypoint.sh

# Switch to the non-root user
USER app

# Note: collectstatic moved to runtime via entrypoint script
# because it requires DATABASE_URL and SECRET_KEY environment variables

# Expose the port the app runs on
EXPOSE 8000

# Run the application via entrypoint script
CMD ["./entrypoint.sh"]