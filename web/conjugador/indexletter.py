#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2019-2020 Jordi Mas i Hernandez <jmas@softcatala.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import json
import logging

from elasticsearch import Elasticsearch
from pyuca import Collator


class IndexLetter:
    """
    Search a letter in the Elasticsearch index.

    Args:
        letter (str): The letter to search for.
        es_url (str | None): The url to connect to an Elasticsearch instance.
    """

    DEFAULT_ES_HOST = "http://localhost:9200"

    def __init__(self, letter: str, es_url: str | None = None) -> None:
        """
        Initializes the IndexLetter class with a letter to look for.

        Args:
            letter (str): The letter to search for.
            es_url (str | None): The url to connect to an Elasticsearch instance.
        """
        if not es_url:
            es_url = self.DEFAULT_ES_HOST

        self.letter = letter
        self.es_client = Elasticsearch(es_url)
        self.index_name = "letter-index"
        self.collator = Collator()
        self.num_results = 0
        self.results = []

    def get_num_results(self) -> int:
        """
        Retrieves the number of results found.

        Returns:
            int: Num of results.
        """
        return self.num_results

    def get_results(self) -> list[dict]:
        """
        Gets the results from the prepared query, based on the letter.

        Returns:
            list[dict]: A list of dicts containing the results.
        """
        if not self.es_client.indices.exists(index=self.index_name):
            self.results = []
            self.num_results = 0
            return self.results

        query = {
            "query": {"term": {"index_letter.keyword": self.letter}},
            "collapse": {"field": "verb_form.keyword"},
            "size": 10000,
            "_source": ["verb_form", "infinitive"],
        }

        try:
            response = self.es_client.search(index=self.index_name, body=query)
            hits = response["hits"]["hits"]
            self.results = [hit["_source"] for hit in hits]
            self.results.sort(
                key=lambda x: self.collator.sort_key(x["verb_form"])
            )
            self.num_results = len(self.results)

        except Exception as e:
            logging.error(f"Error searching index {self.index_name}: {e}")
            self.results = []
            self.num_results = 0

        return self.results

    def get_json(self) -> tuple[str, int]:
        """
        Gets a stringified JSON for all the results found for the initialized
        letter.

        Returns:
            tuple[str, int]: A tuple containing the stringified JSON and the status code.
        """
        OK = 200
        status = OK
        results = self.get_results()
        all_results = []
        for result in results:
            verb = {"verb_form": result["verb_form"]}
            if result["verb_form"] != result["infinitive"]:
                verb["infinitive"] = result["infinitive"]
            all_results.append(verb)

        return json.dumps(
            all_results, indent=4, separators=(",", ": ")
        ), status
