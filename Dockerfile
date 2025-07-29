# ---- Builder Stage: Installs dependencies ----
FROM python:3.13-slim-bookworm AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --retries 3 --timeout 60 -r requirements.txt


FROM python:3.13-slim-bookworm

RUN apt-get update && \
    # Install curl to fetch gosu, and libpq5 for postgres connectivity
    apt-get install -y --no-install-recommends libpq5 curl && \
    rm -rf /var/lib/apt/lists/*

# Install gosu for easy privilege dropping
RUN set -eux; \
    curl -o /usr/local/bin/gosu -sL "https://github.com/tianon/gosu/releases/download/1.17/gosu-$(dpkg --print-architecture)"; \
    chmod +x /usr/local/bin/gosu

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN addgroup --system app && adduser --system --group app

COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV

WORKDIR /home/app/web

COPY --chown=app:app . .
RUN chmod +x ./entrypoint.sh

# Note: collectstatic moved to runtime via entrypoint script
# because it requires DATABASE_URL and SECRET_KEY environment variables

EXPOSE 8000

# The container will start as root, and the entrypoint script
# will use gosu to drop privileges to the 'app' user before running the server.
ENTRYPOINT ["/home/app/web/entrypoint.sh"]
CMD ["gunicorn", "grateful_for.wsgi:application", "--bind", "0.0.0.0:8000"]