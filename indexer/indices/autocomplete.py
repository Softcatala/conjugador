from elasticsearch import helpers

from indexer.firstletter import FirstLetter
from indexer.indices.base import BaseIndex
from indexer.indices.errors import IndexationError


class AutocompleteIndex(BaseIndex):
    """
    Creates multiple autocompletion indexes based on every letter of the catalan alphabet,
    allowing full-text search.

    Args:
        es_url (str | None): Elasticsearch instance url. Defaults to 'DEFAULT_ES_HOST'.
    """

    def __init__(self, es_url: str | None = None) -> None:
        """
        Initializes an AutocompleteIndex instance for the autocompletion feature
        based off Elasticsearch.

        Args:
            es_url (str | None): Elasticsearch instance url. Defaults to 'DEFAULT_ES_HOST'.
        """
        if not es_url:
            es_url = self.DEFAULT_ES_HOST

        super().__init__(es_url)
        self.index_prefix = "autocomplete-"
        self.letter = FirstLetter()
        self.bulk_ops = []
        self.duplicates = set()
        self.created_indices = set()

    def _ensure_index(self, letter: str) -> str:
        """
        Ensures that an index for the given letter exists in the Elasticsearch instance.
        Does not allow duplicate indices and if it does not exist, it creates it right away.

        Args:
            letter (str): The letter for which to create an index.

        Returns:
            str: The full name of the index in the form of 'autocomplete-{letter}'.
        """
        index_name = f"{self.index_prefix}{letter}"
        if index_name not in self.created_indices:
            mapping = self._build_mapping()
            self.create_index(index_name, mapping)
            self.created_indices.add(index_name)

        return index_name

    def _build_mapping(self) -> dict:
        """
        Builds the necessary mappings for creating an index for the autocomplete feature.
        Creates the following fields:
            - verb_form
            - infinitive
            - url
            - autocomplete_sorting
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
                        "fields": {
                            "keyword": {"type": "keyword"},
                        },
                    },
                    "infinitive": {"type": "keyword", "index": False},
                    "url": {"type": "keyword", "index": False},
                    "autocomplete_sorting": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                }
            },
        }

    def write_entry(
        self,
        verb_form: str,
        infinitive: str,
        mode: str,
        tense: str,
        title: str,
        *,
        is_infinitive: bool,
    ) -> None:
        """
        Writes an entry of a verb, tied to a letter index, to the list of bulk operations
        to apply later.

        Args:
            verb_form (str): The verb form to index.
            infinitive (str): The infinitive form of the verb.
            mode (str): The mode of the verb.
            tense (str): The tense of the verb.
            title (str): The title of the entry.
            is_infinitive (bool): Whether the form is an infinitive or not (auxiliar).
        """
        if self._verbs_to_ignore_in_autocomplete(mode, tense):
            return

        letter = self.letter.from_word(verb_form)
        if letter not in self.letter.get_letters():
            raise IndexationError(
                f"Letter {letter} is not supported by the client. Review get_letters()"
            )

        index_name = self._ensure_index(letter)
        sorting_key = self._get_autocomplete_sorting_key(
            verb_form, infinitive, is_infinitive=is_infinitive
        )

        if sorting_key in self.duplicates:
            return

        self.duplicates.add(sorting_key)
        self.bulk_ops.append(
            {
                "_index": index_name,
                "_source": {
                    "verb_form": verb_form,
                    "infinitive": title,
                    "url": infinitive,
                    "autocomplete_sorting": sorting_key,
                },
            }
        )

    def _get_autocomplete_sorting_key(
        self, verb_form: str, infinitive: str, *, is_infinitive: bool
    ) -> str:
        SORTING_PREFIX = "_"
        if is_infinitive:
            # By starting with '_', it forces infinitives to appear first in search
            return f"{SORTING_PREFIX}{infinitive}"

        return f"{verb_form}{SORTING_PREFIX}{infinitive}"

    def save(self) -> None:
        """
        Sends all queued documents via bulk API to index them into Elasticsearch
        instance.
        """
        if not self.bulk_ops:
            raise IndexationError(
                "Cannot bulk index an empty list of operations."
            )

        helpers.bulk(self.es_client, self.bulk_ops)
        self.bulk_ops = []

    def doc_count(self) -> int:
        """
        Gets the total count of the documents in the Autocomplete index.

        Returns:
            int: The total counts of documents in the index.
        """
        total = 0
        for index_name in self.created_indices:
            total += self.es_client.count(index=index_name)["count"]
        return total
