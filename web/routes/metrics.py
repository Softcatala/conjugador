import datetime
import os

import psutil
from fastapi import APIRouter, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from web.monitoring.telemetry import (
    AUTOCOMPLETE_CACHE_HITS_GAUGE,
    AUTOCOMPLETE_CACHE_MISSES_GAUGE,
    INDEX_CACHE_HITS_GAUGE,
    INDEX_CACHE_MISSES_GAUGE,
    MEM_GAUGE,
    SEARCH_CACHE_HITS_GAUGE,
    SEARCH_CACHE_MISSES_GAUGE,
    UPTIME_GAUGE,
)
from web.routes.autocomplete import _get_autocomplete
from web.routes.index import _get_letter_index
from web.routes.search import _get_search

router = APIRouter(prefix="/metrics")


@router.get(
    path="",
    summary="Returns metrics collected throughout the app for Prometheus.",
)
def metrics(request: Request) -> Response:
    """
    TODO: Docstring this.
    """
    rss = int(psutil.Process(os.getpid()).memory_info().rss // 1024**2)
    MEM_GAUGE.set(rss)
    startup_time = request.app.state.start_time
    uptime_seconds = (datetime.datetime.now() - startup_time).total_seconds()
    UPTIME_GAUGE.set(uptime_seconds)
    search_cache = _get_search.cache_info()
    index_cache = _get_letter_index.cache_info()
    autocomplete_cache = _get_autocomplete.cache_info()
    SEARCH_CACHE_HITS_GAUGE.set(search_cache.hits)
    SEARCH_CACHE_MISSES_GAUGE.set(search_cache.misses)
    INDEX_CACHE_HITS_GAUGE.set(index_cache.hits)
    INDEX_CACHE_MISSES_GAUGE.set(index_cache.misses)
    AUTOCOMPLETE_CACHE_HITS_GAUGE.set(autocomplete_cache.hits)
    AUTOCOMPLETE_CACHE_MISSES_GAUGE.set(autocomplete_cache.misses)
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
