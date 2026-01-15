import asyncio
import json
from functools import lru_cache

from fastapi import APIRouter, Request, status

from web.conjugador.autocomplete import Autocomplete
from web.models.autocomplete import AutocompleteEntry, AutocompleteResponse

router = APIRouter(prefix="/autocomplete")


async def _get_autocomplete_uncached(
    word: str, ac: Autocomplete
) -> tuple[str, int]:
    j, status = await ac.get_json(word)
    return j, status


@lru_cache(maxsize=500)
def _get_autocomplete(word: str, ac: Autocomplete) -> tuple[str, int]:
    return asyncio.create_task(_get_autocomplete_uncached(word, ac))


@router.get(
    path="/{word}",
    summary="Provides a list of suggested autocompletions based on the given word",
    response_description="A list of autocompletions with all their information.",
    responses={200: {"description": "The request was fulfilled successfully"}},
    status_code=status.HTTP_200_OK,
)
async def get_autocomplete_results(
    request: Request, word: str
) -> AutocompleteResponse:
    """
    Provides a list of suggested autocompletions of the given word in the format
    of:
        - verb_form
        - infinitive
        - url
    """
    ac = request.app.state.autocomplete
    j, _ = await _get_autocomplete(word, ac)
    resp = [
        AutocompleteEntry(
            verb_form=entry["verb_form"],
            infinitive=entry["infinitive"],
            url=entry["url"],
        )
        for entry in json.loads(j)
    ]
    return resp
