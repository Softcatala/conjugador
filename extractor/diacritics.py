#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 Jordi Mas i Hernandez <jmas@softcatala.org>
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


class Diacritics:
    """
    Contains all the deprecated IEC diacritic accents to identify
    obsolete diacritics and how the word is written nowadays.
    """

    def __init__(self) -> None:
        """
        Initializes a Diacritics instance with defaults.
        """
        self.diacritics = set()

    def load_diacritics(self) -> None:
        """
        Loads from a file all the no longer accepted diacrítics from IEC.
        """
        COMMENT = "#"
        FILENAME = "replace_diacritics_iec.txt"

        diacritics = set()

        if Path(FILENAME).exists():
            filename = FILENAME
        else:
            filename = Path("extractor") / FILENAME

        with Path(filename).open() as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if line[0] == COMMENT:
                continue

            src, _ = line.split("=")
            diacritics.add(src)

        print(f"Read {len(diacritics)} diacritics")
        self.diacritics = diacritics

    def has_word_diacritic(self, word: str) -> bool:
        """
        Returns whether a given word or set of words is in the list of
        deprecated diacrític accents.

        Args:
            word (str): The specific word, or set of words separated by "/".

        Returns:
            bool: Whether the word/s have a deprecated diacrític accent.
        """
        TWO_WORDS_SEPARATOR = "/"

        if TWO_WORDS_SEPARATOR in word:
            words = word.split(TWO_WORDS_SEPARATOR)
        else:
            words = [word]

        for word in words:
            word = word.strip()
            if word in self.diacritics:
                return True

        return False
