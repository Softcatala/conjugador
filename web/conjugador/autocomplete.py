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

from elasticsearch import AsyncElasticsearch

from indexer.firstletter import FirstLetter


class Autocomplete:
    """
    Autocomplete a word based on the information on the Elasticsearch indices.

    Args:
        es_client (AsyncElasticsearch): The client to use for the connection.
    """

    def __init__(self, es_client: AsyncElasticsearch) -> None:
        """
        Initializes the Autocomplete class with a word to autocomplete.

        Args:
            es_client (AsyncElasticsearch): The client to use for the connection.
        """
        self.es_client = es_client
        self.letter = FirstLetter()

    async def get_results(self, word: str) -> list[dict]:
        """
        Gets the results from the prepared query, based on the word to autocomplete.

        Args:
            word (str): The word from which to autocomplete.

        Returns:
            list[dict]: A list of dictionaries containing the results.
        """
        letter = self.letter.from_word(word)
        index_name = f"autocomplete-{letter}"

        if not await self.es_client.indices.exists(index=index_name):
            return []

        query = {
            "query": {
                "prefix": {"verb_form.keyword": {"value": word.lower()}}
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
            resp = await self.es_client.search(index=index_name, body=query)
            results = [hit["_source"] for hit in resp["hits"]["hits"]]
        except Exception as e:
            logging.error(f"Error searching index '{index_name}': {e}")
            results = []

        return results

    async def get_json(self, word: str) -> tuple[str, int]:
        """
        Gets a stringified JSON for all the results found for the autocomplete word.

        Args:
            word (str): The word from which to autocomplete.

        Returns:
            tuple[str, int]: A tuple containing the stringified JSON and the status code.
        """
        OK = 200
        status = OK
        results = await self.get_results(word)

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
