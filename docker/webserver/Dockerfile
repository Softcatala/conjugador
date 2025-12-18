FROM debian:bookworm-slim
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y make bzip2 curl
COPY --from=ghcr.io/astral-sh/uv:0.9.13 /uv /uvx /bin/

COPY pyproject.toml uv.lock /srv/
COPY .python-version /srv/
COPY Makefile /srv/
WORKDIR /srv
RUN uv python install $(cat .python-version)
RUN uv sync
COPY docker/webserver/entrypoint.sh /srv/
COPY catalan-dict-tools /srv/catalan-dict-tools
COPY definitions /srv/definitions
COPY indexer /srv/indexer
COPY extractor /srv/extractor
RUN make generate-data-without-indexation
COPY web /srv/web

ENTRYPOINT /srv/entrypoint.sh
