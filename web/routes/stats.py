import datetime
import os
from functools import _CacheInfo

import psutil
from fastapi import APIRouter, Request

from web.routes.autocomplete import _get_autocomplete
from web.routes.index import _get_letter_index
from web.routes.search import _get_search
from web.monitoring.usage import Usage

router = APIRouter(prefix="/stats")


def _get_cache_info(cache_info: _CacheInfo) -> dict:
    cache = {}

    hits = cache_info.hits
    misses = cache_info.misses

    total = hits + misses
    phits = (hits * 100 / total) if total else 0

    cache["misses"] = f"{misses}"
    cache["hits"] = f"{hits} ({phits:.2f}%)"
    return cache


@router.get(path="/")
def stats(request: Request, date: str) -> dict:
    """
    TODO: Docstring this endpoint.
    """
    start_time = request.app.state.start_time
    try:
        date_requested = datetime.datetime.strptime(date, "%Y-%m-%d")
    except Exception:
        return {}

    usage = Usage()
    result = usage.get_stats(date_requested)
    rss = psutil.Process(os.getpid()).memory_info().rss // 1024**2

    caches = {}
    caches["search"] = _get_cache_info(_get_search.cache_info())
    caches["letter_index"] = _get_cache_info(_get_letter_index.cache_info())
    caches["autocomplete"] = _get_cache_info(_get_autocomplete.cache_info())
    result["cache"] = caches

    result["process_id"] = os.getpid()
    result["rss"] = f"{rss} MB"
    result["up_time"] = str(datetime.datetime.now() - start_time)
    return result
