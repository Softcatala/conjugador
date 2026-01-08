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

from web.conjugador.base import BaseSearch


class Search(BaseSearch):
    """
    Search a term in the Elasticsearch search index.

    Args:
        word (str): The word to search for.
        es_url (str | None): The url to connect to an Elasticsearch instance.
    """

    def __init__(self, word: str, es_url: str | None = None) -> None:
        """
        Initializes the Search class with a word to look into an Elasticsearch index.

        Args:
            word (str): The word to search for.
            es_url (str | None): The url to connect to an Elasticsearch instance.
        """
        if not es_url:
            es_url = self.DEFAULT_ES_HOST

        super().__init__(word, es_url)
        self.query = None
        self.query_expansion = None
        self.num_results = 0
        self.results = []
        self.index_name = "search-index"

    def get_num_results(self) -> int:
        """
        Retrieves the number of results found.

        Returns:
            int: Num of results.
        """
        return self.num_results

    async def get_results(self) -> list[dict]:
        """
        Gets the results from the prepared query.

        Returns:
            Results: A wrapper over a list of dicts containing the results.
        """
        if not await self.es_client.indices.exists(index=self.index_name):
            self.results = []
            self.num_results = 0
            return self.results

        query = {
            "query": {"match": {"verb_form": {"query": self.word}}},
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
                        "match": {
                            "verb_form_no_diacritics": {"query": self.word}
                        }
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
                self.results = []
                self.num_results = 0
                return self.results

            self.results = [hit["_source"] for hit in hits]
            self.num_results = len(self.results)
        except Exception as e:
            logging.error(f"Error searching index '{self.index_name}': {e}")
            self.results = []
            self.num_results = 0

        return self.results

    async def get_json_search(self) -> tuple[str, int]:
        """
        Gets a stringified JSON for all the results found for the initialized
        word.

        Returns:
            tuple[str, int]: A tuple containing the stringified JSON and the status code.
        """
        OK = 200

        status = OK
        results = await self.get_results()

        # This close is a temporary shortcut to avoid memory leaks for leaving connections open.
        # This will be solved in the future with a single shared client for all the app and not using word
        # on constructor but rather as function argument.
        await self.es_client.close()

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
