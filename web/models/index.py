from pydantic import BaseModel


class IndexEntry(BaseModel):  # noqa: D101
    verb_form: str
    infinitive: str | None = None


type IndexResponse = list[IndexEntry]
