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

from web.firstletter import FirstLetter
from web.models.base import BaseSearch


class Autocomplete(BaseSearch):
    """
    Autocomplete a word based on the information on the Elasticsearch indices.

    Args:
        word (str): The word to try to autocomplete from.
        es_url (str): The url to connect to an Elasticsearch instance.
    """

    def __init__(self, word: str, es_url: str | None = None) -> None:
        """
        Initializes the Autocomplete class with a word to autocomplete.

        Args:
            word (str): The word to try to autocomplete from.
            es_url (str | None): The url to connect to an Elasticsearch instance.
        """
        if not es_url:
            es_url = self.DEFAULT_ES_HOST

        super().__init__(word, es_url)
        self.query = None
        self.num_results = 0
        self.letter = FirstLetter()
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
        Gets the results from the prepared query, based on the word to autocomplete.

        Returns:
            list[dict]: A list of dictionaries containing the results.
        """
        letter = self.letter.from_word(self.word)
        index_name = f"autocomplete-{letter}"

        if not self.es_client.indices.exists(index=index_name):
            self.results = []
            self.num_results = 0
            return self.results

        query = {
            "query": {
                "prefix": {"verb_form.keyword": {"value": self.word.lower()}}
            },
            "sort": [
                {
                    "autocomplete_sorting.keyword": {
                        "order": "asc",
                    },
                },
            ],
            "size": 1000,
            "_source": ["verb_form", "infinitive", "url"],
        }

        try:
            resp = self.es_client.search(index=index_name, body=query)
            self.results = [hit["_source"] for hit in resp["hits"]["hits"]]
            self.num_results = len(self.results)
        except Exception as e:
            logging.error(f"Error searching index '{index_name}': {e}")
            self.results = []
            self.num_results = 0

        return self.results

    def get_json(self) -> tuple[str, int]:
        """
        Gets a stringified JSON for all the results found for the initialized
        autocomplete word.

        Returns:
            tuple[str, int]: A tuple containing the stringified JSON and the status code.
        """
        OK = 200
        status = OK
        results = self.get_results()
        all_results = []
        for result in results:
            verb = {
                "verb_form": result["verb_form"],
                "infinitive": result["infinitive"],
                "url": result["url"],
            }
            all_results.append(verb)

        return json.dumps(
            all_results, indent=4, separators=(",", ": ")
        ), status
