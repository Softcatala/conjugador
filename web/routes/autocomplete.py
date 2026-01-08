import asyncio
import json
import os
from functools import lru_cache

from fastapi import APIRouter, status

from web.conjugador.autocomplete import Autocomplete
from web.models.autocomplete import AutocompleteEntry, AutocompleteResponse

router = APIRouter(prefix="/autocomplete")


async def _get_autocomplete_uncached(word: str) -> tuple[str, int, int]:
    es_url = os.getenv("ES_URL", "http://conjugador-elastic:9200")
    autocomplete = Autocomplete(word, es_url)
    j, status = await autocomplete.get_json()
    num_results = autocomplete.get_num_results()
    return j, status, num_results


@lru_cache(maxsize=500)
def _get_autocomplete(word: str) -> tuple[str, int, int]:
    return asyncio.create_task(_get_autocomplete_uncached(word))


@router.get(
    path="/{word}",
    summary="Provides a list of suggested autocompletions based on the given word",
    response_description="A list of autocompletions with all their information.",
    responses={200: {"description": "The request was fulfilled successfully"}},
    status_code=status.HTTP_200_OK,
)
async def get_autocomplete_results(word: str) -> AutocompleteResponse:
    """
    Provides a list of suggested autocompletions of the given word in the format
    of:
        - verb_form
        - infinitive
        - url
    """
    j, _, _ = await _get_autocomplete(word)
    resp = [
        AutocompleteEntry(
            verb_form=entry["verb_form"],
            infinitive=entry["infinitive"],
            url=entry["url"],
        )
        for entry in json.loads(j)
    ]
    return resp
