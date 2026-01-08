import datetime
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from web.monitoring.logging import init_logging
from web.routes import autocomplete, index, search, stats


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN201, D103
    app.state.start_time = datetime.datetime.now()
    init_logging()
    yield


app = FastAPI(lifespan=lifespan)

es_logger = logging.getLogger("elastic_transport.transport")
es_logger.setLevel(os.getenv("LOGLEVEL", "WARNING"))

app.include_router(index.router)
app.include_router(autocomplete.router)
app.include_router(search.router)
app.include_router(stats.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
    allow_credentials=True,
)


@app.get("/")
def read_root() -> dict:  # noqa: D103
    return {"message": "Softcatalà Conjugador API"}
