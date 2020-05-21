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

from whoosh.fields import TEXT, Schema
from whoosh.index import create_in
from index import Index
from whoosh.analysis import CharsetFilter
from whoosh.support.charset import accent_map
from firstletter import FirstLetter

class Search(Index):

    def __init__(self):
        super(Search, self).__init__()
        self.dir_name_search = "data/search_index/"
        self.writer = None
        self.letter = FirstLetter()

    def create(self):
        analyzer_no_diatritics = self.analyzer | CharsetFilter(accent_map)
        schema = Schema(verb_form=TEXT(stored=True, sortable=True, analyzer=self.analyzer),
                        verb_form_no_diacritics=TEXT(analyzer=analyzer_no_diatritics),
                        index_letter=TEXT(sortable=True, analyzer=self.analyzer),
                        file_path=TEXT(stored=True, sortable=True))

        self._create_dir(self.dir_name_search)
        ix = create_in(self.dir_name_search, schema)
        self.writer = ix.writer()

    def write_entry(self, verb_form, file_path, is_infinitive, infinitive, mode, tense):

        if self._verbs_to_ignore_in_autocomplete(mode, tense):
            return

        if is_infinitive:
            index_letter =  self.letter.form_word(verb_form)
        else:
            index_letter = None

        self.writer.add_document(verb_form = verb_form,
                                 verb_form_no_diacritics = verb_form,
                                 file_path = file_path,
                                 index_letter = index_letter)

    def save(self):
        self.writer.commit()
