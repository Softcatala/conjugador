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
# Boston, MA 02111-1307, USA.

from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser
import json
from searchbase import SearchBase


dir_name = "../data/search_index/"
ix = open_dir(dir_name) # static instance reusable across requests

class Search(SearchBase):
    """Search a term in the Whoosh index."""

    def __init__(self, word):
        self._word = word
        self.searcher = None
        self.query = None
        self.query_expansion = None

    def get_results(self):
        if self.searcher is None:
            self.search()

        results = self.searcher.search(self.query, limit=None,
                                    sortedby='index_letter',
                                    collapse='file_path')

        if results.is_empty():
            results = self.searcher.search(self.query_expansion, limit=None,
                                    sortedby='index_letter',
                                    collapse='file_path')
        return results

    def search(self):

        self.searcher = ix.searcher()
        fields = []
        qs = u' verb_form:({0})'.format(self._word)
        self.query = MultifieldParser(fields, ix.schema).parse(qs)

        qs = u' verb_form_no_diacritics:({0})'.format(self._word)
        self.query_expansion = MultifieldParser(fields, ix.schema).parse(qs)

    def get_json_search(self):
        OK = 200

        status = OK
        results = self.get_results()
        all_results = []
        for result in results:

            filepath = "../" + result['file_path']

            with open(filepath, 'r') as j:
                file = json.loads(j.read())
                all_results.append(file)

        return json.dumps(all_results, indent=4, separators=(',', ': ')), status
