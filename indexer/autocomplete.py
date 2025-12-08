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

from whoosh.fields import STORED, TEXT, Schema
from whoosh.index import create_in
from whoosh.multiproc import MpWriter
from whoosh.writing import SegmentWriter

from indexer.firstletter import FirstLetter
from indexer.index import Index


class Autocomplete(Index):
    """
    Creates a filesystem Whoosh-based index for the Autocompletion feature, that allows
    for full-text search and stores entries in disk.
    """

    def __init__(self) -> None:
        """
        Initializes a filesystem Whoosh-based index for the Autocompletion feature.
        """
        super().__init__()
        self.dir_name = "data/autocomplete_index/"
        self.writers = {}
        self.letter = FirstLetter()
        self.ixs = set()
        self.duplicates = set()

    def _create(self, letter: str) -> MpWriter | SegmentWriter:
        schema = Schema(
            verb_form=TEXT(stored=True, analyzer=self.analyzer),
            infinitive=STORED,
            url=STORED,
            autocomplete_sorting=TEXT(sortable=True),
        )

        dir_name = f"{self.dir_name}{letter}/"
        self._create_dir(dir_name)
        ix = create_in(dir_name, schema)
        self.ixs.add(ix)
        return ix.writer()

    def doc_count(self) -> int:
        """
        Gets the total count of the documents in the Autocomplete index.

        Returns:
            int: The total counts of documents in the index.
        """
        count = 0
        for ix in self.ixs:
            count += ix.doc_count()

        return count

    def write_entry(
        self,
        verb_form: str,
        _file_path: str,
        infinitive: str,
        mode: str,
        tense: str,
        title: str,
        *,
        is_infinitive: bool,
    ) -> None:
        """
        Writes an entry of a verb to the Autocomplete index.

        Args:
            verb_form (str): The verb form to write.
            file_path (str): Not used.
            is_infinitive (bool): Whether the form is an infinitive or not (auxiliar).
            mode (str): The mode of the verb.
            tense (str): The tense of the verb.
            title (str): The title of the entry.
        """
        if self._verbs_to_ignore_in_autocomplete(mode, tense):
            return

        letter = self.letter.from_word(verb_form)
        if letter not in self.letter.get_letters():
            raise IndexError(
                f"Letter {letter} is not supported by the client. Review get_letters()"
            )

        if letter in self.writers:
            writer = self.writers[letter]
        else:
            writer = self._create(letter)
            self.writers[letter] = writer

        autocomplete_sorting = self._get_autocomple_sorting_key(
            verb_form, infinitive, is_infinitive=is_infinitive
        )

        if autocomplete_sorting in self.duplicates:
            return

        self.duplicates.add(autocomplete_sorting)

        writer.add_document(
            verb_form=verb_form,
            infinitive=title,
            url=infinitive,
            autocomplete_sorting=autocomplete_sorting,
        )

    def _get_autocomple_sorting_key(
        self, verb_form: str, infinitive: str, *, is_infinitive: bool
    ) -> str:
        SORTING_PREFIX = "_"
        if is_infinitive:
            # By starting with '_', it forces infinitives to appear first in search
            return f"{SORTING_PREFIX}{infinitive}"

        return f"{verb_form}{SORTING_PREFIX}{infinitive}"

    def save(self) -> None:
        """
        Commits all the scheduled document insertions to the Autocomplete index.
        """
        for writer in self.writers.values():
            writer.commit()
