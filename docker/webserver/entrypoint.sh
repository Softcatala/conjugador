#!/bin/sh
mkdir -p /var/log/conjugador/
mkdir -p /tmp/prometheus_multiproc
uv run gunicorn web.web_search:app -b 0.0.0.0:8000 --error-logfile /var/log/conjugador/gnuicorn.log --workers=2
