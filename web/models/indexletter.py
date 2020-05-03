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

from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser
from whoosh.sorting import FieldFacet, TranslateFacet
import json
from pyuca import Collator
from searchbase import SearchBase


dir_name = "../data/indexletter_index/"
ix_letter = open_dir(dir_name) # static instance reusable across requests

class IndexLetter(SearchBase):

    def __init__(self, word):
        self._word = word
        self.searcher = None
        self.query = None
        self.collator = Collator()

    def sort_key(self, string):
        s = string.decode("utf-8")
        return self.collator.sort_key(s)

    def get_results(self):
        if self.searcher is None:
            self.search()

        facet = FieldFacet("verb_form")
        facet = TranslateFacet(self.sort_key, facet)

        return self.searcher.search(self.query,
                                    limit=None,
                                    sortedby=facet,
                                    collapse_limit=1,
                                    collapse='verb_form')

    def search(self):
        self.searcher = ix_letter.searcher()
        fields = []
        qs = u'index_letter:({0})'.format(self.word)
        fields.append("index_letter")
        self.query = MultifieldParser(fields, ix_letter.schema).parse(qs)

    def get_json(self):
        OK = 200
        status = OK
        results = self.get_results()
        all_results = []
        for result in results:
            verb = result['verb_form']
            all_results.append(verb)

        return json.dumps(all_results, indent=4, separators=(',', ': ')), status
