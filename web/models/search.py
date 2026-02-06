from pydantic import BaseModel, RootModel


class SearchVerbConjugation(BaseModel):  # noqa: D101
    word: str
    variant: str


class SearchVerbInformation(BaseModel):  # noqa: D101
    mode: str
    tense: str
    postag: str
    singular1: list[SearchVerbConjugation]
    singular2: list[SearchVerbConjugation]
    singular3: list[SearchVerbConjugation]
    plural1: list[SearchVerbConjugation]
    plural2: list[SearchVerbConjugation]
    plural3: list[SearchVerbConjugation]


class SearchVerbMetadata(BaseModel):  # noqa: D101
    definition: str | None = None
    definition_credits: str
    title: str
    infinitive: str
    note: str | None = None


type VerbEntry = SearchVerbInformation | SearchVerbMetadata


class SearchResponse(  # noqa: D101
    RootModel[list[dict[str, list[VerbEntry]]]]
):
    pass
