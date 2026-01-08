import json
import os
from functools import lru_cache

from fastapi import APIRouter

from web.conjugador.search import Search
from web.models.search import (
    SearchResponse,
)

router = APIRouter(prefix="/search")


@lru_cache(maxsize=500)  # Rationale: there are ~10K infitives, cache top 5%
def _get_search(word: str) -> tuple[str, int, int]:
    es_url = os.getenv("ES_URL", "http://conjugador-elastic:9200")
    search = Search(word, es_url)
    j, status = search.get_json_search()
    num_results = search.get_num_results()
    return j, status, num_results


@router.get(path="/{word}")
async def get_search_results(word: str) -> SearchResponse:
    """
    TODO: Docstring this endpoint.
    """
    j, _, _ = _get_search(word)
    return SearchResponse.model_validate(json.loads(j))
