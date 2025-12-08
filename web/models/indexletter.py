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
from typing import Any

from pyuca import Collator
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser
from whoosh.searching import Results, Searcher
from whoosh.sorting import FieldFacet, TranslateFacet

dir_name = "data/indexletter_index/"
ix_letter = open_dir(dir_name)  # static instance reusable across requests


class IndexLetter:
    """
    Search a letter in the Whoosh index.

    Args:
        letter (str): The letter to search for.
    """

    def __init__(self, letter: str) -> None:
        """
        Initializes the IndexLetter class with a letter to look for.

        Args:
            letter (str): The letter to search for.
        """
        self.letter = letter
        self.searcher: Searcher | None = None
        self.query = None
        self.collator = Collator()
        self.num_results = 0

    def get_num_results(self) -> int:
        """
        Retrieves the number of results found.

        Returns:
            int: Num of results.
        """
        return self.num_results

    def _sort_key(self, string: Any) -> tuple:
        s = string.decode("utf-8")
        return self.collator.sort_key(s)

    def get_results(self) -> Results:
        """
        Gets the results from the prepared query, based on the letter.

        Returns:
            Results: A wrapper over a list of dicts containing the results.
        """
        if self.searcher is None:
            self.search()

        facet = FieldFacet("verb_form")
        facet = TranslateFacet(self._sort_key, facet)

        results = self.searcher.search(  # pyrefly: ignore
            self.query,
            limit=None,
            sortedby=facet,
            collapse_limit=1,
            collapse="verb_form",
        )

        self.num_results = len(results)
        return results

    def search(self) -> None:
        """
        Performs a search based on the initialized letter.
        """
        self.searcher = ix_letter.searcher()
        fields = []
        qs = "index_letter:({0})".format(self.letter)
        fields.append("index_letter")
        self.query = MultifieldParser(fields, ix_letter.schema).parse(qs)

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
            verb = {}
            verb["verb_form"] = result["verb_form"]
            if result["verb_form"] != result["infinitive"]:
                verb["infinitive"] = result["infinitive"]
            all_results.append(verb)

        return json.dumps(
            all_results, indent=4, separators=(",", ": ")
        ), status
