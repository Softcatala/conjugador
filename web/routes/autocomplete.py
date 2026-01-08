import json
from functools import lru_cache

from fastapi import APIRouter
from web.models.autocomplete import Autocomplete

router = APIRouter(prefix="/autocomplete")


@lru_cache(maxsize=500)
def _get_autocomplete(word: str) -> tuple[str, int, int]:
    autocomplete = Autocomplete(word, "http://conjugador-elastic:9200")
    j, status = autocomplete.get_json()
    num_results = autocomplete.get_num_results()
    return j, status, num_results


@router.get(path="/{word}")
async def get_autocomplete_results(word: str) -> list[dict]:
    """
    TODO: Docstring this endpoint.
    """
    j, _, _ = _get_autocomplete(word)
    return json.loads(j)
