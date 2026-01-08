import json
import os
from functools import lru_cache

from fastapi import APIRouter

from web.conjugador.indexletter import IndexLetter
from web.models.index import IndexEntry, IndexResponse

router = APIRouter(prefix="/index")


@lru_cache(maxsize=23)  # Rationale: there 23 index files only
def _get_letter_index(letter: str) -> tuple[str, int, int]:
    es_url = os.getenv("ES_URL", "http://conjugador-elastic:9200")
    indexLetter = IndexLetter(letter, es_url)
    j, status = indexLetter.get_json()
    num_results = indexLetter.get_num_results()
    return j, status, num_results


@router.get(
    path="/{letter}",
    response_model_exclude_none=True,
)
async def get_index_results(letter: str) -> IndexResponse:
    """
    TODO: Docstring this endpoint.
    """
    j, _, _ = _get_letter_index(letter)
    resp = [
        IndexEntry(
            verb_form=entry["verb_form"], infinitive=entry.get("infinitive")
        )
        for entry in json.loads(j)
    ]
    return resp
