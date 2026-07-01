FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# system deps (safe baseline for yfinance/backtrader/pandas builds)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . .

RUN pip install --no-cache-dir ".[server]"

# ---- runtime image ----
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# copy venv
COPY --from=builder /opt/venv /opt/venv

# create non-root user + required directory
RUN useradd --create-home appuser \
 && mkdir -p /home/appuser/.tradingagents \
 && chown -R appuser:appuser /home/appuser

WORKDIR /home/appuser/app

COPY --from=builder --chown=appuser:appuser /build .

USER appuser

# Cloud Run expects port 8080
EXPOSE 8080

# IMPORTANT: start HTTP server, NOT CLI
CMD ["python", "server.py"]
