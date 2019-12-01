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

from whoosh.highlight import WholeFragmenter
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser
from whoosh.query import FuzzyTerm
import json
import cgi

class Search(object):
    """Search a term in the Whoosh index."""
    dir_name = "../indexdir"

    def __init__(self, word):
        self._word = word
        self.searcher = None
        self.query = None

    @property
    def word(self):
        return self._word

    def get_results(self):
        if self.searcher is None:
            self.search()

        results = self.searcher.search(self.query, limit=None, reverse=True)    
        return results

    def search(self, ix=None):
        if ix is None:
            ix = open_dir(self.dir_name)
            self.search(ix)

        self.searcher = ix.searcher()
        fields = []
        qs = ''

        qs += u' verb_form:({0})'.format(self._word)
        self.query = MultifieldParser(fields, ix.schema).parse(qs)

    def get_json(self):
        return self._get_json_search()

    def _get_json_search(self):
        OK = 200
        NOT_FOUND = 404

        status = OK
        results = self.get_results()
        all_results = []
        for result in results:
            all_results.append(result.fields())

        return json.dumps(all_results, indent=4, separators=(',', ': ')), status

    def _get_result(self, result, key):
        if key in result:
            return cgi.escape(result[key]) 

        return None
