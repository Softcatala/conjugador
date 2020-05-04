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

class IndexLetter(Index):

    def __init__(self):
        super(IndexLetter, self).__init__()
        self.dir_name = "data/indexletter_index/"
        self.writer = None
        self.entries = 0

    def create(self):
        schema = Schema(verb_form=TEXT(stored=True, sortable=True, analyzer=self.analyzer),
                        index_letter=TEXT(sortable=True, analyzer=self.analyzer),
                        infinitive=TEXT(stored=True, analyzer=self.analyzer))

        self._create_dir(self.dir_name)
        ix = create_in(self.dir_name, schema)
        self.writer = ix.writer()

    def write_entry(self, verb_form, is_infinitive, infinitive):
        if is_infinitive:
            index_letter = self._get_first_letter_for_index(verb_form)
        else:
            index_letter = None

        if index_letter is not None:
            self.entries = self.entries + 1
            self.writer.add_document(verb_form = verb_form,
                                     index_letter = index_letter,
                                     infinitive = infinitive)


    def save(self):
        self.writer.commit()
