import asyncio
import json
from functools import lru_cache

from fastapi import APIRouter, Request, status

from web.conjugador.indexletter import IndexLetter
from web.models.index import IndexEntry, IndexResponse
from web.monitoring.telemetry import REQUEST_COUNTER

router = APIRouter(prefix="/index")


async def _get_letter_index_uncached(
    letter: str, ix: IndexLetter
) -> tuple[str, int]:
    j, status = await ix.get_json(letter)
    return j, status


@lru_cache(maxsize=23)  # Rationale: there 23 index files only
def _get_letter_index(letter: str, ix: IndexLetter) -> tuple[str, int]:
    return asyncio.create_task(_get_letter_index_uncached(letter, ix))


@router.get(
    path="/{letter}",
    response_model_exclude_none=True,
    summary="Provides a list of all the verb forms and infinitives present that start with a letter.",
    response_description="A list of all the known verb forms and infinitives that start with a letter.",
    responses={200: {"description": "The request was fulfilled successfully"}},
    status_code=status.HTTP_200_OK,
)
async def get_index_results(request: Request, letter: str) -> IndexResponse:
    """
    Provides a list of all the known verb forms and their infinitives that start
    with the given letter.
    """
    REQUEST_COUNTER.labels(endpoint="/index/{letter}", method="GET").inc()
    ix = request.app.state.index_letter
    j, _ = await _get_letter_index(letter, ix)
    resp = [
        IndexEntry(
            verb_form=entry["verb_form"], infinitive=entry.get("infinitive")
        )
        for entry in json.loads(j)
    ]
    return resp
