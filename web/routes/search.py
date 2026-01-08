import asyncio
import json
import os
from functools import lru_cache

from fastapi import APIRouter, status

from web.conjugador.search import Search
from web.models.search import SearchResponse

router = APIRouter(prefix="/search")


async def _get_search_uncached(word: str) -> tuple[str, int, int]:
    es_url = os.getenv("ES_URL", "http://conjugador-elastic:9200")
    search = Search(word, es_url)
    j, status = await search.get_json_search()
    num_results = search.get_num_results()
    return j, status, num_results


@lru_cache(maxsize=500)  # Rationale: there are ~10K infitives, cache top 5%
def _get_search(word: str) -> tuple[str, int, int]:
    return asyncio.create_task(_get_search_uncached(word))


@router.get(
    path="/{word}",
    summary="Returns a list of all verbs and their information that match the given word.",
    response_description="A list of all verbs and information and conjugations.",
    responses={200: {"description": "The request was fulfilled successfully"}},
    status_code=status.HTTP_200_OK,
)
async def get_search_results(word: str) -> SearchResponse:
    """
    Returns a list of all verbs and their information that match the given word.
    """
    j, _, _ = await _get_search(word)
    return SearchResponse.model_validate(json.loads(j))
