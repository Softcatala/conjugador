#!/bin/sh
mkdir -p /var/log/conjugador/
uv run uvicorn web.main:app --host 0.0.0.0 --port 8000 --log-level error 2>>/var/log/conjugador/uvicorn_error.log
