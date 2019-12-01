#/bin/sh
cd /conjugador/web
gunicorn web_search:app -b 0.0.0.0:8000
