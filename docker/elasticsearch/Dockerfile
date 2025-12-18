FROM elasticsearch:8.15.1 as build
USER root
RUN apt-get update && \
    apt-get install -y bzip2 make procps httping curl && \
    rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:0.9.13 /uv /uvx /bin/

RUN mkdir -p /srv
COPY pyproject.toml uv.lock Makefile /srv/
COPY indexer /srv/indexer
COPY extractor /srv/extractor
COPY definitions /srv/definitions
COPY catalan-dict-tools /srv/catalan-dict-tools
WORKDIR /srv
COPY .python-version /srv/

RUN uv python install $(cat .python-version) && \
    uv sync

ENV discovery.type=single-node
ENV xpack.security.enabled=false
ENV ES_JAVA_OPTS="-Xms512m -Xmx512m"

# Start Elasticsearch, wait for health, run indexing, then stop
RUN set -e && \
    runuser -u elasticsearch -- /usr/share/elasticsearch/bin/elasticsearch -d -p /tmp/es.pid && \
    echo "Waiting for Elasticsearch to be ready..." && \
    for i in $(seq 1 180); do \
        if curl -s http://localhost:9200/_cluster/health 2>/dev/null | grep -q '"status":"green\|yellow"'; then \
            echo "Elasticsearch is ready!"; \
            break; \
        fi; \
        if [ $i -eq 180 ]; then \
            echo "Elasticsearch failed to start"; \
            exit 1; \
        fi; \
        echo "Waiting... ($i/180)"; \
        sleep 2; \
    done && \
    make generate-data; \
    MAKE_EXIT_CODE=$?; \
    echo "Flushing data to disk..." && \
    curl -X POST "http://localhost:9200/_flush" 2>/dev/null || true && \
    sleep 2 && \
    echo "Shutting down Elasticsearch..." && \
    if [ -f /tmp/es.pid ]; then \
        ES_PID=$(cat /tmp/es.pid); \
        kill -TERM $ES_PID 2>/dev/null || true; \
        for i in $(seq 1 60); do \
            if ! kill -0 $ES_PID 2>/dev/null; then \
                echo "Elasticsearch stopped cleanly"; \
                break; \
            fi; \
            if [ $i -eq 60 ]; then \
                echo "Force killing Elasticsearch"; \
                kill -9 $ES_PID 2>/dev/null || true; \
            fi; \
            sleep 1; \
        done; \
    fi && \
    sleep 3 && \
    echo "Removing lock files..." && \
    find /usr/share/elasticsearch/data -name "*.lock" -type f -delete && \
    find /usr/share/elasticsearch/data -name "write.lock" -type f -delete && \
    if [ $MAKE_EXIT_CODE -ne 0 ]; then \
        echo "ERROR: make generate-data failed with exit code $MAKE_EXIT_CODE"; \
        exit $MAKE_EXIT_CODE; \
    fi && \
    echo "Indexing complete!"

FROM elasticsearch:8.15.1
USER root
COPY --from=build /usr/share/elasticsearch/data /usr/share/elasticsearch/data
RUN chown -R elasticsearch:elasticsearch /usr/share/elasticsearch/data
ENV discovery.type=single-node
ENV xpack.security.enabled=false
ENV ES_JAVA_OPTS="-Xms512m -Xmx512m"
USER elasticsearch
