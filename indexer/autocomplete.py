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

from whoosh.fields import TEXT, Schema, STORED
from whoosh.index import create_in
from index import Index
from firstletter import FirstLetter

class Autocomplete(Index):

    def __init__(self):
        super(Autocomplete, self).__init__()
        self.dir_name = "data/autocomplete_index/"
        self.writers = {}
        self.letter = FirstLetter()
        self.ixs = set()
        self.duplicates = set()

    def create(self):
        return

    def _create(self, letter):
        schema = Schema(verb_form=TEXT(stored=True, analyzer=self.analyzer),
                        infinitive=STORED,
                        autocomplete_sorting=TEXT(sortable=True))

        dir_name = f'{self.dir_name}{letter}/'
        self._create_dir(dir_name)
        ix = create_in(dir_name, schema)
        self.ixs.add(ix)
        return ix.writer()

    def doc_count(self):
        count = 0
        for ix in self.ixs:
            count += ix.doc_count()

        return count


    def write_entry(self, verb_form, file_path, is_infinitive, infinitive, mode, tense):

        if self._verbs_to_ignore_in_autocomplete(mode, tense):
            return

        letter = self.letter.from_word(verb_form)
        if letter not in self.letter.get_letters():
              raise IndexError(f'Letter {letter} is not supported by the client. Review get_letters()')

        if letter in self.writers:
            writer = self.writers[letter]
        else:
            writer = self._create(letter)
            self.writers[letter] = writer
    
        autocomplete_sorting = self._get_autocomple_sorting_key(verb_form, is_infinitive, infinitive)

        if autocomplete_sorting in self.duplicates:
            return

        self.duplicates.add(autocomplete_sorting)

        writer.add_document(verb_form = verb_form,
                                 infinitive = infinitive,
                                 autocomplete_sorting = autocomplete_sorting)

    def _get_autocomple_sorting_key(self, verb_form, is_infinitive, infinitive):
        SORTING_PREFIX='_'
        if is_infinitive:
            # By starting with '_', it forces infinitives to appear first in search
            return f'{SORTING_PREFIX}{infinitive}'
        else:
            return f'{verb_form}{SORTING_PREFIX}{infinitive}'

    def save(self):
        for writer in self.writers.values():
            writer.commit()
