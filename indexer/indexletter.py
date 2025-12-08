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
from whoosh.multiproc import MpWriter
from whoosh.writing import SegmentWriter

from indexer.firstletter import FirstLetter
from indexer.index import Index


class IndexLetter(Index):
    """
    Creates a filesystem Whoosh-based index for the IndexLetter index feature,
    that allows to query all the verbs starting with the specified index letter.
    """

    def __init__(self) -> None:
        """
        Initializes a filesystem Whoosh-based index for the IndexLetter feature,
        with the values it needs, like the default directory where to store it...
        """
        super().__init__()
        self.dir_name = "data/indexletter_index/"
        self.writer: MpWriter | SegmentWriter | None = None
        self.entries = 0
        self.letter = FirstLetter()

    def create(self) -> None:
        """
        Builds and creates the verb letter index in the filesystem with the following
        fields:
            - verb_form
            - index_letter
            - infinitive
        """
        schema = Schema(
            verb_form=TEXT(stored=True, sortable=True, analyzer=self.analyzer),
            index_letter=TEXT(sortable=True, analyzer=self.analyzer),
            infinitive=TEXT(stored=True, analyzer=self.analyzer),
        )

        self._create_dir(self.dir_name)
        ix = create_in(self.dir_name, schema)
        self.writer = ix.writer()

    def write_entry(
        self,
        verb_form: str,
        infinitive: str,
        title: str,
        *,
        is_infinitive: bool,
    ) -> None:
        """
        Writes an entry of a verb to the IndexLetter index.

        Args:
            verb_form (str): The verb form to write.
            infinitive (str): The infinitive of the verb.
            title (str): The title of the entry.
            is_infinitive (bool): Whether the form is an infinitive or not (auxiliar).
        """
        if is_infinitive:
            index_letter = self.letter.from_word(verb_form)
        else:
            index_letter = None

        if index_letter is not None:
            self.entries = self.entries + 1
            if verb_form == infinitive and infinitive != title:
                verb_form = title

            if self.writer:
                self.writer.add_document(
                    verb_form=verb_form,
                    index_letter=index_letter,
                    infinitive=infinitive,
                )

    def save(self) -> None:
        """
        Commits all the scheduled document insertions to the IndexLetter index.
        """
        if self.writer:
            self.writer.commit()
        else:
            raise AttributeError(
                "IndexLetter instance hasn't got an initialized writer!"
            )
