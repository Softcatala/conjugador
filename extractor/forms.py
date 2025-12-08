#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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


class Form:
    """
    Defines a specific conjugation of a word, known as a Form.

    Args:
        word (str): The word to conjugate.
        variant (str): The variant to apply to the word.
        prefix (str | None): The prefix which to apply to the word.
        diacritic (bool): Whether the form has a diacrític or not.
    """

    def __init__(
        self,
        word: str,
        variant: str,
        prefix: str | None = None,
        *,
        diacritic: bool = False,
    ) -> None:
        """
        Initializes a Form with a word, variant, prefix and whether it incorporates
        a diacritic accent or not.

        Args:
            word (str): The word to conjugate.
            variant (str): The variant to apply to the word.
            prefix (str | None): The prefix which to apply to the word.
            diacritic (bool): Whether the form has a diacrític or not.
        """
        if prefix is None:
            prefix = ""

        self.word = prefix + word
        self.variant = variant
        if diacritic:
            self.diacritic = diacritic

    def __str__(self) -> str:
        """Represents a Form in a string format."""
        return "{0} - {1} ".format(self.word, self.variant)


class Tense:
    """
    Describes a verbal tense with the mode, tense, postag (M, A, S),
    and all the conjugations.

    Args:
        mode (str): Gramatical mode.
        tense (str): Verbal tense.
        postag (str): The postag representing the tense.
    """

    def __init__(self, mode: str, tense: str, postag: str) -> None:
        """
        Initializes a tense with a mode, verbal tense and postag.

        Args:
            mode (str): Gramatical mode.
            tense (str): Verbal tense.
            postag (str): The postag representing the tense.
        """
        self.mode = mode
        self.tense = tense
        self.postag = postag
        self.singular1 = []
        self.singular2 = []
        self.singular3 = []
        self.plural1 = []
        self.plural2 = []
        self.plural3 = []

    def __str__(self) -> str:
        """Represents a Tense in a string format."""
        s = "---"
        s += "* {0} ({1})\n".format(self.tense, self.mode)
        s += "{0}\n".format("".join(str(p) for p in self.singular1))
        s += "{0}\n".format("".join(str(p) for p in self.singular2))
        s += "{0}\n".format("".join(str(p) for p in self.singular3))
        s += "{0}\n".format("".join(str(p) for p in self.plural1))
        s += "{0}\n".format("".join(str(p) for p in self.plural2))
        s += "{0}\n".format("".join(str(p) for p in self.plural3))
        return s
