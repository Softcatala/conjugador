#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2019 Jordi Mas i Hernandez <jmas@softcatala.org>
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
# Boston, MA02111-1307, USA.

import asyncio
import json
import logging

import aiofiles
from elasticsearch import AsyncElasticsearch


class Search:
    """
    Search a term in the Elasticsearch search index.

    Args:
        es_client (AsyncElasticsearch): The client with which to connect to the ES instance.
    """

    def __init__(self, es_client: AsyncElasticsearch) -> None:
        """
        Initializes the Search class with a preconfigured ES client.

        Args:
            es_client (AsyncElasticsearch): The client with which to connect to the ES instance.
        """
        self.es_client = es_client
        self.index_name = "search-index"

    async def get_results(self, word: str) -> list[dict]:
        """
        Gets the results from the prepared query based off the word..

        Args:
            word (str): The word to search for.

        Returns:
            Results: A wrapper over a list of dicts containing the results.
        """
        if not await self.es_client.indices.exists(index=self.index_name):
            return []

        query = {
            "query": {"match": {"verb_form": {"query": word}}},
            "sort": [{"index_letter.keyword": {"order": "asc"}}],
            "collapse": {"field": "file_path.keyword"},
            "size": 10000,
            "_source": True,
        }

        try:
            resp = await self.es_client.search(
                index=self.index_name, body=query
            )
            hits = resp["hits"]["hits"]
            if len(hits) == 0:
                query_expansion = {
                    "query": {
                        "match": {"verb_form_no_diacritics": {"query": word}}
                    },
                    "sort": [{"index_letter.keyword": {"order": "asc"}}],
                    "collapse": {"field": "file_path.keyword"},
                    "size": 10000,
                    "_source": True,
                }
                response = await self.es_client.search(
                    index=self.index_name, body=query_expansion
                )
                hits = response["hits"]["hits"]
            if len(hits) == 0:
                return []

            results = [hit["_source"] for hit in hits]
        except Exception as e:
            logging.error(f"Error searching index '{self.index_name}': {e}")
            results = []

        return results

    async def get_json_search(self, word: str) -> tuple[str, int]:
        """
        Gets a stringified JSON for all the results found for the given word.

        Args:
            word (str): The word to search for.

        Returns:
            tuple[str, int]: A tuple containing the stringified JSON and the status code.
        """
        OK = 200

        status = OK
        results = await self.get_results(word)

        async def _read_file_async(filepath: str) -> dict | None:
            try:
                async with aiofiles.open(filepath, "r") as f:
                    content = await f.read()
                    return json.loads(content)
            except Exception as e:
                logging.error(f"Error reading file {filepath}: {e}")
                return None

        tasks = [_read_file_async(result["file_path"]) for result in results]

        all_results = await asyncio.gather(*tasks)

        return json.dumps(
            all_results, indent=4, separators=(",", ": ")
        ), status
