from elasticsearch import Elasticsearch


class BaseIndex:
    """
    Base Index class that provides basic shared functionality between indices.

    Args:
        es_url (str | None): The connection url of the Elasticsearch instance.
    """

    DEFAULT_ES_HOST = "http://localhost:9200"

    def __init__(self, es_url: str | None = None) -> None:
        """
        Initializes a BaseIndex instance with an Elasticsearch client and
        a catalan tokenizer pattern.

        Args:
            es_url (str | None): The connection url of the Elasticsearch instance.
        """
        if not es_url:
            es_url = self.DEFAULT_ES_HOST

        self.es_client = Elasticsearch(es_url)

        if not self.es_client.ping():
            raise AttributeError("Invalid Elasticsearch URL provided.")

        self.tokenizer_pattern = r"(\w|·)+(\.?(\w|·)+)*"

    def create_index(self, index_name: str, mappings: dict) -> None:
        """
        Creates an index with the specified name and body mappings.
        If it's already created, deletes it and recreates it.

        Args:
            index_name (str): The name of the index to create.
            mappings (dict): A dictionary containing the body mappings of the index.
        """
        if self.es_client.indices.exists(index=index_name):
            self.es_client.indices.delete(index=index_name)

        self.es_client.indices.create(index=index_name, body=mappings)

    def _verbs_to_ignore_in_autocomplete(self, mode: str, tense: str) -> bool:
        if mode == "Indicatiu" and any(
            t in tense
            for t in [
                "Perfet",
                "Plusquamperfet",
                "Passat perifràstic",
                "Passat anterior",
                "Passat anterior perifràstic",
                "Futur perfet",
                "Condicional perfet",
            ]
        ):
            return True

        if mode == "Subjuntiu" and any(
            t in tense for t in ["Perfet", "Plusquamperfet"]
        ):
            return True

        return bool(
            mode == "Formes no personals"
            and any(
                t in tense for t in ["Infinitiu compost", "Gerundi compost"]
            )
        )
