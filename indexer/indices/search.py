from elasticsearch import helpers

from indexer.firstletter import FirstLetter
from indexer.indices.base import BaseIndex
from indexer.indices.errors import IndexationError


class SearchIndex(BaseIndex):
    """
    Creates a Search index allowing to check verbs based off a given search text.

    Args:
        es_url (str | None): Elasticsearch instance url. Defaults to 'DEFAULT_ES_HOST'.
    """

    def __init__(self, es_url: str | None = None) -> None:
        """
        Initializes a SearchIndex instance for the letter feature based off Elasticsearch.

        Args:
            es_url (str | None): Elasticsearch instance url. Defaults to 'DEFAULT_ES_HOST'.
        """
        if not es_url:
            es_url = self.DEFAULT_ES_HOST

        super().__init__(es_url)
        self.index_name = "search-index"
        self.letter = FirstLetter()
        self.bulk_ops = []

    def _build_mapping(self) -> dict:
        """
        Builds the necessary mappings for creating an index for the search feature.
        Creates the following fields:
            - verb_form
            - verb_form_no_diacritics
            - index_letter
            - file_path
        Also attaches a custom tokenizer based on a regex pattern and a custom analyzer for
        checking every term in lowercase, and a custom analyzer for diacritics.

        Returns:
            dict: A dictionary containing the mappings to create an index.
        """
        return {
            "settings": {
                "analysis": {
                    "tokenizer": {
                        "custom_catalan_tokenizer": {
                            "type": "pattern",
                            "pattern": self.tokenizer_pattern,
                        }
                    },
                    "analyzer": {
                        "custom_catalan_analyzer": {
                            "type": "custom",
                            "tokenizer": "custom_catalan_tokenizer",
                            "filter": ["lowercase"],
                        },
                        "custom_catalan_no_diacritics_analyzer": {
                            "type": "custom",
                            "tokenizer": "custom_catalan_tokenizer",
                            "filter": ["lowercase", "asciifolding"],
                        },
                    },
                }
            },
            "mappings": {
                "properties": {
                    "verb_form": {
                        "type": "text",
                        "analyzer": "custom_catalan_analyzer",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "verb_form_no_diacritics": {
                        "type": "text",
                        "analyzer": "custom_catalan_no_diacritics_analyzer",
                    },
                    "index_letter": {
                        "type": "text",
                        "analyzer": "custom_catalan_analyzer",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "file_path": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                },
            },
        }

    def _ensure_index(self) -> None:
        """
        Ensures that the search index exists in the Elasticsearch instance.
        Does not allow duplicate indices and if it does not exist, it creates it right away.
        """
        if not self.es_client.indices.exists(index=self.index_name):
            self.es_client.indices.create(
                index=self.index_name, body=self._build_mapping()
            )

    def write_entry(
        self,
        verb_form: str,
        file_path: str,
        infinitive: str,
        mode: str,
        tense: str,
        title: str,
        *,
        is_infinitive: bool,
    ) -> None:
        """
        Schedules an insertion operation to write a new entry to the Search index.

        Args:
            verb_form (str): The verb form to write.
            file_path (str): The path to the verb file.
            infinitive (str): The infinitive of the verb.
            mode (str): The mode of the verb.
            tense (str): The verbal tense.
            title (str): The title of the entry.
            is_infinitive (bool): Whether the form is an infinitive or not (auxiliar).
        """
        if self._verbs_to_ignore_in_autocomplete(mode, tense):
            return

        if is_infinitive:
            index_letter = self.letter.from_word(verb_form)
        else:
            index_letter = None

        if verb_form == infinitive and infinitive != title:
            self.bulk_ops.append(
                {
                    "_index": self.index_name,
                    "_source": {
                        "verb_form": title,
                        "verb_form_no_diacritics": title,
                        "file_path": file_path,
                        "index_letter": index_letter,
                    },
                }
            )

        # Don't know why we always have to do this other append no matter what, but
        # the old code did so.
        self.bulk_ops.append(
            {
                "_index": self.index_name,
                "_source": {
                    "verb_form": verb_form,
                    "verb_form_no_diacritics": verb_form,
                    "file_path": file_path,
                    "index_letter": index_letter,
                },
            }
        )

    def save(self) -> None:
        """
        Commits all the scheduled document insertions to the search index.
        """
        if not self.bulk_ops:
            raise IndexationError(
                "Cannot bulk index an empty list of operations"
            )

        helpers.bulk(self.es_client, self.bulk_ops)
        self.bulk_ops = []
