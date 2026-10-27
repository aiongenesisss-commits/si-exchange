# Reproducible Linux runtime for the SI Exchange simulation.
# The Debian base image is downloaded once; pin a digest before production use.
FROM debian:bookworm-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-venv ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m venv /opt/venv

WORKDIR /srv/si-exchange
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements-dev.txt

COPY app ./app
COPY api ./api
COPY tests ./tests
COPY scripts ./scripts
COPY pyproject.toml README.md ./

# Image build is isolated; tests can be run with:
# docker run --rm si-exchange-linux:local python -m pytest
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
