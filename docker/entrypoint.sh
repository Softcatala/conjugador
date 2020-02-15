#/bin/sh
cd srv/web/
mkdir -p /var/log/conjugador/
gunicorn web_search:app -b 0.0.0.0:8000 --error-logfile /var/log/conjugador/gnuicorn.log
