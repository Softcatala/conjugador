from elasticsearch import helpers

from indexer.firstletter import FirstLetter
from indexer.indices.base import BaseIndex
from indexer.indices.errors import IndexationError


class LetterIndex(BaseIndex):
    """
    Creates a Letter index allowing to check verbs based off their first letter.

    Args:
        es_url (str | None): Elasticsearch instance url. Defaults to 'DEFAULT_ES_HOST'.
    """

    def __init__(self, es_url: str | None = None) -> None:
        """
        Initializes a LetterIndex instance for the letter feature
        based off Elasticsearch.

        Args:
            es_url (str | None): Elasticsearch instance url. Defaults to 'DEFAULT_ES_HOST'.
        """
        if not es_url:
            es_url = self.DEFAULT_ES_HOST

        super().__init__(es_url)
        self.index_name = "letter-index"
        self.letter = FirstLetter()
        self.entries = 0
        self.bulk_ops = []

    def _build_mapping(self) -> dict:
        """
        Builds the necessary mappings for creating an index for the letter feature.
        Creates the following fields:
            - verb_form
            - infinitive
            - index_letter
        Also attaches a custom tokenizer based on a regex pattern and a custom analyzer for
        checking every term in lowercase.

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
                        }
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
                    "index_letter": {
                        "type": "text",
                        "analyzer": "custom_catalan_analyzer",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "infinitive": {
                        "type": "text",
                        "analyzer": "custom_catalan_analyzer",
                    },
                }
            },
        }

    def _ensure_index(self) -> None:
        """
        Ensures that the letter index exists in the Elasticsearch instance.
        Does not allow duplicate indices and if it does not exist, it creates it right away.
        """
        if not self.es_client.indices.exists(index=self.index_name):
            self.es_client.indices.create(
                index=self.index_name, body=self._build_mapping()
            )

    def write_entry(
        self,
        verb_form: str,
        infinitive: str,
        title: str,
        *,
        is_infinitive: bool,
    ) -> None:
        """
        Schedules an insertion operation to write a new entry to the Letter index.

        Args:
            verb_form (str): The verb form to write.
            infinitive (str): The infinitive of the verb.
            title (str): The title of the entry.
            is_infinitive (bool): Whether the form is an infinitive or not (auxiliar).
        """
        if is_infinitive:
            index_letter = self.letter.from_word(verb_form)
        else:
            index_letter = None

        if index_letter is not None:
            self.entries = self.entries + 1
            if verb_form == infinitive and infinitive != title:
                verb_form = title

        self.bulk_ops.append(
            {
                "_index": self.index_name,
                "_source": {
                    "verb_form": verb_form,
                    "infinitive": infinitive,
                    "index_letter": index_letter,
                },
            }
        )

    def save(self) -> None:
        """
        Commits all the scheduled document insertions to the letter index.
        """
        if not self.bulk_ops:
            raise IndexationError(
                "Cannot bulk index an empty list of operations"
            )

        helpers.bulk(self.es_client, self.bulk_ops)
        self.bulk_ops = []
