import asyncio
import json
import os
from functools import lru_cache

from fastapi import APIRouter, status

from web.conjugador.indexletter import IndexLetter
from web.models.index import IndexEntry, IndexResponse

router = APIRouter(prefix="/index")


async def _get_letter_index_uncached(letter: str) -> tuple[str, int, int]:
    es_url = os.getenv("ES_URL", "http://conjugador-elastic:9200")
    indexLetter = IndexLetter(letter, es_url)
    j, status = await indexLetter.get_json()
    num_results = indexLetter.get_num_results()
    return j, status, num_results


@lru_cache(maxsize=23)  # Rationale: there 23 index files only
def _get_letter_index(letter: str) -> tuple[str, int, int]:
    return asyncio.create_task(_get_letter_index_uncached(letter))


@router.get(
    path="/{letter}",
    response_model_exclude_none=True,
    summary="Provides a list of all the verb forms and infinitives present that start with a letter.",
    response_description="A list of all the known verb forms and infinitives that start with a letter.",
    responses={200: {"description": "The request was fulfilled successfully"}},
    status_code=status.HTTP_200_OK,
)
async def get_index_results(letter: str) -> IndexResponse:
    """
    Provides a list of all the known verb forms and their infinitives that start
    with the given letter.
    """
    j, _, _ = await _get_letter_index(letter)
    resp = [
        IndexEntry(
            verb_form=entry["verb_form"], infinitive=entry.get("infinitive")
        )
        for entry in json.loads(j)
    ]
    return resp
