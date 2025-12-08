#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Joan Montané <jmontane@softcatala.org>
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
import os
from pathlib import Path


class Notes:
    """
    Loads all the notes for verbs that need clarifications.
    """

    def __init__(self) -> None:
        """Initializes the Notes class with defaults."""
        self.notes = {}

    def load_notes(self) -> None:
        """Loads all the notes from the `notes.json` static file."""
        FILENAME = "notes.json"

        directory = Path(os.path.realpath(__file__)).parent
        filename = directory / FILENAME

        with filename.open() as json_file:
            notes = json.load(json_file)

        print(f"Read {len(notes)} notes")

        self.notes = notes

    def has_note_for(self, lemma: str) -> bool:
        """
        Checks whether a given lemma has an associated note or not.

        Args:
            lemma (str): The lemma to check for.

        Returns:
            bool: Whether it has an associated note.
        """
        return lemma in self.notes

    def get_note(self, lemma: str) -> str | None:
        """
        Retrieves the note for the given lemma if it exists.

        Args:
            lemma (str): The lemma to retrieve the note of.

        Returns:
            str | None: The note if the lemma has it, otherwise None.
        """
        return self.notes.get(lemma, None)
