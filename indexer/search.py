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

from whoosh.analysis import CharsetFilter
from whoosh.fields import TEXT, Schema
from whoosh.index import create_in
from whoosh.multiproc import MpWriter
from whoosh.support.charset import accent_map
from whoosh.writing import SegmentWriter

from indexer.firstletter import FirstLetter
from indexer.index import Index


class Search(Index):
    """
    Creates a filesystem Whoosh-based index for the Search index feature,
    that allows to query all the verbs starting with the provided search.
    """

    def __init__(self) -> None:
        """
        Initializes a filesystem Whoosh-based index for the Search feature,
        with the values it needs, like the default directory where to store it...
        """
        super().__init__()
        self.dir_name_search = "data/search_index/"
        self.writer: MpWriter | SegmentWriter | None = None
        self.letter = FirstLetter()

    def create(self) -> None:
        """
        Builds and creates the verb search index in the filesystem with the following
        fields:
             - verb_form
             - verb_form_no_diacritics
             - index_letter
             - file_path
        """
        analyzer_no_diatritics = self.analyzer | CharsetFilter(accent_map)
        schema = Schema(
            verb_form=TEXT(sortable=True, analyzer=self.analyzer),
            verb_form_no_diacritics=TEXT(analyzer=analyzer_no_diatritics),
            index_letter=TEXT(sortable=True, analyzer=self.analyzer),
            file_path=TEXT(stored=True, sortable=True),
        )

        self._create_dir(self.dir_name_search)
        ix = create_in(self.dir_name_search, schema)
        self.writer = ix.writer()

    def write_entry(
        self,
        verb_form: str,
        file_path: str,
        infinitive: str,
        mode: str,
        tense: str,
        title: str,
        *,
        is_infinitive: bool,
    ) -> None:
        """
        Writes an entry of a verb to the Search index.

        Args:
            verb_form (str): The verb form to write.
            file_path (str): The path to the verb file.
            infinitive (str): The infinitive of the verb.
            mode (str): The mode of the verb.
            tense (str): The verbal tense.
            title (str): The title of the entry.
            is_infinitive (bool): Whether the form is an infinitive or not (auxiliar).
        """
        if self._verbs_to_ignore_in_autocomplete(mode, tense):
            return

        if is_infinitive:
            index_letter = self.letter.from_word(verb_form)
        else:
            index_letter = None

        if verb_form == infinitive and infinitive != title and self.writer:
            self.writer.add_document(
                verb_form=title,
                verb_form_no_diacritics=title,
                file_path=file_path,
                index_letter=index_letter,
            )

        if self.writer:
            self.writer.add_document(
                verb_form=verb_form,
                verb_form_no_diacritics=verb_form,
                file_path=file_path,
                index_letter=index_letter,
            )

    def save(self) -> None:
        """
        Commits all the scheduled document insertions to the Search index.
        """
        if self.writer:
            self.writer.commit()
        else:
            raise AttributeError(
                "IndexLetter instance hasn't got an initialized writer!"
            )
