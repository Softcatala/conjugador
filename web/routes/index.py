import json
from functools import lru_cache

from fastapi import APIRouter
from web.models.indexletter import IndexLetter

router = APIRouter(prefix="/index")


@lru_cache(maxsize=23)  # Rationale: there 23 index files only
def _get_letter_index(letter: str) -> tuple[str, int, int]:
    indexLetter = IndexLetter(letter, "http://conjugador-elastic:9200")
    j, status = indexLetter.get_json()
    num_results = indexLetter.get_num_results()
    return j, status, num_results


@router.get(path="/{letter}")
async def get_index_results(letter: str) -> list[dict]:
    """
    TODO: Docstring this endpoint.
    """
    j, _, _ = _get_letter_index(letter)
    return json.loads(j)
