# FROM python:3.11-slim AS builder

# ENV VIRTUAL_ENV=/opt/venv
# ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# WORKDIR /app

# RUN python -m venv $VIRTUAL_ENV

# COPY pyproject.toml poetry.lock ./

# RUN pip install --no-cache-dir poetry \
#     && poetry config virtualenvs.create false \
#     && poetry install --only main --no-root --no-interaction --no-ansi

# FROM python:3.11-slim AS runtime

# ENV VIRTUAL_ENV=/opt/venv
# ENV PATH="$VIRTUAL_ENV/bin:$PATH"
# ENV PYTHONUNBUFFERED=1

# WORKDIR /app

# RUN useradd --create-home appuser

# COPY --from=builder /opt/venv /opt/venv
# COPY churnguard ./churnguard
# COPY api ./api
# COPY README.md pyproject.toml ./

# USER appuser

# EXPOSE 8000

# HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
#   CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

# CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]


# FROM python:3.11-slim AS builder

# ENV VIRTUAL_ENV=/opt/venv
# ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# WORKDIR /app

# RUN python -m venv $VIRTUAL_ENV

# COPY pyproject.toml poetry.lock ./

# RUN pip install --no-cache-dir poetry poetry-plugin-export \
#     && poetry export -f requirements.txt --only main --without-hashes -o requirements.txt \
#     && pip install --no-cache-dir -r requirements.txt

# FROM python:3.11-slim AS runtime

# ENV VIRTUAL_ENV=/opt/venv
# ENV PATH="$VIRTUAL_ENV/bin:$PATH"
# ENV PYTHONUNBUFFERED=1

# WORKDIR /app

# RUN useradd --create-home appuser

# COPY --from=builder /opt/venv /opt/venv
# COPY churnguard ./churnguard
# COPY api ./api
# COPY README.md pyproject.toml ./

# USER appuser

# EXPOSE 8000

# HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
#   CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

# CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# FROM python:3.11-slim AS builder

# ENV VIRTUAL_ENV=/opt/venv
# WORKDIR /app

# RUN python -m venv $VIRTUAL_ENV

# COPY pyproject.toml poetry.lock ./

# RUN pip install --no-cache-dir poetry poetry-plugin-export \
#     && poetry export -f requirements.txt --only main --without-hashes -o requirements.txt \
#     && $VIRTUAL_ENV/bin/pip install --no-cache-dir -r requirements.txt \
#     && $VIRTUAL_ENV/bin/pip uninstall -y pip setuptools wheel

# FROM python:3.11-slim AS runtime

# ENV VIRTUAL_ENV=/opt/venv
# ENV PATH="$VIRTUAL_ENV/bin:$PATH"
# ENV PYTHONUNBUFFERED=1

# WORKDIR /app

# RUN useradd --create-home appuser

# COPY --from=builder /opt/venv /opt/venv
# COPY churnguard ./churnguard
# COPY api ./api
# COPY README.md pyproject.toml ./

# USER appuser

# EXPOSE 8000

# HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
#   CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

# CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.11-slim AS builder

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app

RUN python -m venv $VIRTUAL_ENV

COPY pyproject.toml poetry.lock ./

RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --only main --no-root --no-interaction --no-ansi

FROM python:3.11-slim AS runtime

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN useradd --create-home appuser

COPY --from=builder /opt/venv /opt/venv
COPY churnguard ./churnguard
COPY api ./api
COPY README.md pyproject.toml ./

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]