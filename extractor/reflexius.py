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

class Reflexius:

    def __init__(self):
        self.reflexius = set()

    def load_reflexius(self):
        FILENAME = 'reflexius.txt'

        directory = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(directory, FILENAME)

        with open(filename) as f:
            reflexius = set([s.strip() for s in f.readlines()])

        print(f"Read {len(reflexius)} reflexius")
        self.reflexius = reflexius

    def get_reflexiu(self, lemma):
        if lemma not in self.reflexius:
            return lemma

        if lemma[-1] == 'e':
            lemma = lemma + "'s"
        else:
            lemma = lemma + "-se"
        return lemma

    def is_reflexiu(self, lemma):
        if lemma in self.reflexius:
            return True
        else:
            return False
