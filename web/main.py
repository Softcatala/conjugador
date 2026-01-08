import os
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from web.routes import autocomplete, index, search

app = FastAPI()

es_logger = logging.getLogger("elastic_transport.transport")
es_logger.setLevel(os.getenv("LOGLEVEL", "WARNING"))

app.include_router(index.router)
app.include_router(autocomplete.router)
app.include_router(search.router)

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
