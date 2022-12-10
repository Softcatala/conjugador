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
                    
'''
    Reads a plain text file with forms that we need to ignore
'''

class ExclusionsFile:

    def __init__(self, exclusion_file):
        self.lemmas = self._process_exclusions(exclusion_file)

    def get_lemmas(self):
        return self.lemmas

    def _read_file(self, input_file):
        with open(input_file) as f:
            return f.readlines()

    def _process_exclusions(self, exclusion_file):
        lemmas = set()
        if len(exclusion_file) > 0:
            exclude_lemmas = self._read_file(exclusion_file)
            for lemma in exclude_lemmas:
                lemma = lemma.lower().strip()
                if len(lemma) == 0:
                    continue

                if lemma[0] == "#":
                    continue

                lemmas.add(lemma)

        print(f"Read exclusions {len(lemmas)}")
        return lemmas
