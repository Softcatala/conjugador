import asyncio
import json
from functools import lru_cache

from fastapi import APIRouter, Request, status

from web.conjugador.search import Search
from web.models.search import SearchResponse

router = APIRouter(prefix="/search")


async def _get_search_uncached(word: str, search: Search) -> tuple[str, int]:
    j, status = await search.get_json_search(word)
    return j, status


@lru_cache(maxsize=500)  # Rationale: there are ~10K infitives, cache top 5%
def _get_search(word: str, search: Search) -> tuple[str, int]:
    return asyncio.create_task(_get_search_uncached(word, search))


@router.get(
    path="/{word}",
    summary="Returns a list of all verbs and their information that match the given word.",
    response_description="A list of all verbs and information and conjugations.",
    responses={200: {"description": "The request was fulfilled successfully"}},
    status_code=status.HTTP_200_OK,
)
async def get_search_results(request: Request, word: str) -> SearchResponse:
    """
    Returns a list of all verbs and their information that match the given word.
    """
    search = request.app.state.search
    j, _ = await _get_search(word, search)
    return SearchResponse.model_validate(json.loads(j))
