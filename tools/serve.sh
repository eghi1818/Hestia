#!/usr/bin/env bash
# Jalankan layanan Hestia. Satu origin: API dan dashboard.
set -uo pipefail
cd "$(dirname "$0")/.."
mkdir -p .out data
exec .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8787
