#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 Jordi Mas i Hernandez <jmas@softcatala.org>
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

from pathlib import Path


class ExclusionsFile:
    """
    Loads a given file containing forms to exclude from a dictionary.

    Args:
        exclusion_file_path (str): The path to the file containing the lemmas.
    """

    def __init__(self, exclusion_file_path: str) -> None:
        """
        Initializes the ExclusionsFile by reading the excluded forms from
        a given file path.

        Args:
            exclusion_file_path (str): The path to the file with the excluded lemmas.
        """
        self.lemmas = self._process_exclusions(exclusion_file_path)

    def get_lemmas(self) -> set[str]:
        """
        Gets all the processed lemmas to exclude.

        Returns:
            set[str]: A set containing the lemmas in the exclusions file.
        """
        return self.lemmas

    def _read_file(self, file_path: str) -> list[str]:
        with Path(file_path).open() as f:
            return f.readlines()

    def _process_exclusions(self, exclusion_file_path: str) -> set[str]:
        """
        Generates a set of unique lemmas to exclude based on a file that contains
        them. Ignores all comments and empty lines but does not safely check that
        the line is a lemma.

        Args:
            exclusion_file_path (str): The path to the file containing the lemmas
            to exclude.

        Returns:
            set[str]: A set with all the lemmas to exclude.
        """
        lemmas = set()
        if len(exclusion_file_path) > 0:
            exclude_lemmas = self._read_file(exclusion_file_path)
            for lemma in exclude_lemmas:
                lemma = lemma.lower().strip()
                if len(lemma) == 0:
                    continue

                if lemma[0] == "#":
                    continue

                lemmas.add(lemma)

        print(f"Read exclusions {len(lemmas)}")
        return lemmas
