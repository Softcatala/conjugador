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

import os
from pathlib import Path


class Reflexius:
    """
    Loads all the reflexive verbs in catalan and attaches the correct suffix.
    """

    def __init__(self) -> None:
        """Initializes the Reflexius class"""
        self.reflexius = set()

    def load_reflexius(self) -> None:
        """Loads all the reflexive verbs from the `reflexius.txt` file."""
        FILENAME = "reflexius.txt"

        directory = Path(os.path.realpath(__file__)).parent
        filename = directory / FILENAME

        with filename.open() as f:
            reflexius = {s.strip() for s in f.readlines()}

        print(f"Read {len(reflexius)} reflexius")
        self.reflexius = reflexius

    def get_reflexiu(self, lemma: str) -> str:
        """
        Gets the reflexive form of a given lemma if it exists, otherwise returns
        the same lemma.

        Args:
            lemma (str): The lemma to get the reflexive form of.

        Returns:
            str: The reflexive form of the lemma or the lemma itself.
        """
        if lemma not in self.reflexius:
            return lemma

        lemma = lemma + "'s" if lemma[-1] == "e" else lemma + "-se"
        return lemma
