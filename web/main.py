import datetime
import logging
import os
from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from web.conjugador.autocomplete import Autocomplete
from web.conjugador.indexletter import IndexLetter
from web.conjugador.search import Search
from web.monitoring.logging import init_logging
from web.routes import autocomplete, index, metrics, search, stats


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN201, D103
    app.state.start_time = datetime.datetime.now()
    es_client = AsyncElasticsearch(
        os.getenv("ES_URL", "http://conjugador-elastic:9200")
    )
    app.state.autocomplete = Autocomplete(es_client)
    app.state.index_letter = IndexLetter(es_client)
    app.state.search = Search(es_client)
    init_logging()

    yield

    await app.state.autocomplete.es_client.close()
    await app.state.index_letter.es_client.close()
    await app.state.search.es_client.close()


app = FastAPI(lifespan=lifespan)

es_logger = logging.getLogger("elastic_transport.transport")
es_logger.setLevel(os.getenv("LOGLEVEL", "WARNING"))

app.include_router(index.router)
app.include_router(autocomplete.router)
app.include_router(search.router)
app.include_router(stats.router)
app.include_router(metrics.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
    allow_credentials=True,
)


@app.get("/")
def root() -> dict:  # noqa: D103
    return {"message": "Softcatalà Conjugador API"}
