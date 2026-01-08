import json
from functools import lru_cache

from fastapi import APIRouter
from web.models.search import Search

router = APIRouter(prefix="/search")


@lru_cache(maxsize=500)  # Rationale: there are ~10K infitives, cache top 5%
def _get_search(word: str) -> tuple[str, int, int]:
    search = Search(word, "http://conjugador-elastic:9200")
    j, status = search.get_json_search()
    num_results = search.get_num_results()
    return j, status, num_results


@router.get(path="/{word}")
async def get_search_results(word: str) -> list[dict]:
    """
    TODO: Docstring this endpoint.
    """
    j, _, _ = _get_search(word)
    return json.loads(j)
