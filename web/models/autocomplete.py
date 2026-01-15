from pydantic import BaseModel


class AutocompleteEntry(BaseModel):  # noqa: D101
    verb_form: str
    infinitive: str
    url: str


type AutocompleteResponse = list[AutocompleteEntry]
