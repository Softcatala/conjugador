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
from pyuca import Collator


class IndexLetter:
    """
    Search a letter in the Elasticsearch index.

    Args:
        es_client (AsyncElasticsearch): The client to use for the ES connection.
    """

    def __init__(self, es_client: AsyncElasticsearch) -> None:
        """
        Initializes the IndexLetter class with a preconfigured ES client.

        Args:
            es_client (AsyncElasticsearch): The client to use for the ES connection.
        """
        self.es_client = es_client
        self.index_name = "letter-index"
        self.collator = Collator()

    async def get_results(self, letter: str) -> list[dict]:
        """
        Gets the results from the prepared query, based on the letter.

        Args:
            letter (str): The letter of the index to check.

        Returns:
            list[dict]: A list of dicts containing the results.
        """
        if not await self.es_client.indices.exists(index=self.index_name):
            return []

        query = {
            "query": {"term": {"index_letter.keyword": letter}},
            "collapse": {"field": "verb_form.keyword"},
            "size": 10000,
            "_source": ["verb_form", "infinitive"],
        }

        try:
            response = await self.es_client.search(
                index=self.index_name, body=query
            )
            hits = response["hits"]["hits"]
            results = [hit["_source"] for hit in hits]
            results.sort(key=lambda x: self.collator.sort_key(x["verb_form"]))

        except Exception as e:
            logging.error(f"Error searching index {self.index_name}: {e}")
            results = []

        return results

    async def get_json(self, letter: str) -> tuple[str, int]:
        """
        Gets a stringified JSON for all the results found for the given letter.

        Args:
            letter (str): The letter of the index to check.

        Returns:
            tuple[str, int]: A tuple containing the stringified JSON and the status code.
        """
        OK = 200
        status = OK
        results = await self.get_results(letter)

        all_results = []
        for result in results:
            verb = {"verb_form": result["verb_form"]}
            if result["verb_form"] != result["infinitive"]:
                verb["infinitive"] = result["infinitive"]
            all_results.append(verb)

        return json.dumps(
            all_results, indent=4, separators=(",", ": ")
        ), status
