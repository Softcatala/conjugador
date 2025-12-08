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


class FirstLetter:
    """
    Utility class to get the equivalent ASCII letter of a given word.
    """

    def __init__(self) -> None:
        """
        Initializes the FirstLetter instance with all the valid ASCII chars.
        """
        self.valid_letters = list(map(chr, range(97, 123)))

    def from_word(self, word: str) -> str:
        """
        Gets the first character of a word, translating any accentuated character
        to its valid ASCII format.

        Args:
            word (str): The word from whom to get the parsed first char.

        Returns:
            str: A character representing the first letter of the word, parsed.
        """
        s = ""
        if word is None or len(word) == 0:
            return s

        s = word[0].lower()
        mapping = {
            "à": "a",
            "è": "e",
            "é": "e",
            "í": "i",
            "ó": "o",
            "ò": "o",
            "ú": "u",
        }

        if s in mapping:
            s = mapping[s]

        return s

    def get_letters(self) -> list[str]:
        """
        Gets all the accepted letters in ASCII format.

        Returns:
            list[str]: A list of the accepted letters.
        """
        return self.valid_letters
