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
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN addgroup --system app && adduser --system --group app

COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV

WORKDIR /home/app/web

COPY --chown=app:app . .

COPY --chown=app:app entrypoint.sh .
RUN chmod +x entrypoint.sh

USER app

# Note: collectstatic moved to runtime via entrypoint script
# because it requires DATABASE_URL and SECRET_KEY environment variables

EXPOSE 8000

CMD ["./entrypoint.sh"]