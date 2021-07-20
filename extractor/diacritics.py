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

import os

class Diacritics:

    def __init__(self):
        self.diacritics = set()

    def load_diacritics(self):
        COMMENT = '#'
        FILENAME = 'replace_diacritics_iec.txt'

        diacritics = set()

        if os.path.exists(FILENAME):
            filename = FILENAME
        else:
            filename = os.path.join("extractor/", f"{FILENAME}")

        with open(filename) as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if line[0] == COMMENT:
                continue

            src, trg = line.split('=')
            diacritics.add(src)

        print(f"Read {len(diacritics)} diacritics")
        self.diacritics = diacritics

    def has_word_diacritic(self, word):

        TWO_WORDS_SEPARATOR = '/'

        if TWO_WORDS_SEPARATOR in word:
            words = word.split(TWO_WORDS_SEPARATOR)
        else:
            words = [word]

        for word in words:
            word = word.strip()
            if word in self.diacritics:
                return True

        return False
