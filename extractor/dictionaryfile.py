#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019-2022 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import re
'''
    Reads a dictionary text file with entries with the following format:

        form lemma postag
        cantaria cantar VMIC1S00

    Makes the data accessible in the form of: form, lemma and postag.
'''
class DictionaryFile:

    def __init__(self, filename):
        lines = self._read_file(filename)
        self.lines = self._pre_process_anar_auxiliar(lines)

    def get_form_lemma_postag(self):
        for line in self.lines:
            form, lemma, postag = self._get_form_lemma_postag_from_line(line)
            yield form, lemma, postag

    def get_lemmas_for_infinitives(self):

        INFINITIVE_DESCRIPTORS = set(['VMN00000', 'VAN00000', 'VSN00000'])

        lemmas = []
        for line in self.lines:
            form, lemma, postag = self._get_form_lemma_postag_from_line(line)

            if postag not in INFINITIVE_DESCRIPTORS:
                continue

            lemmas.append(lemma)

        return lemmas

    def _read_file(self, input_file):
        with open(input_file) as f:
            return f.readlines()

    '''
        La forma en infinitiu "anar" no és una forma auxiliar i no apareix com a infinitiu al diccionari.
        Com a resultat totes les formes vaja, vam, van queden penjades sense mostrar-se.
    '''
    def _pre_process_anar_auxiliar(self, lines):
        for i in range(0, len(lines)):
            line = lines[i]
            form, lemma, postag = self._get_form_lemma_postag_from_line(line)

            if lemma =='anar' and postag[0:2] == 'VA':
                line = f'{form} anar_aux {postag}'
                lines[i] = line

        lines.append("anar anar_aux VAN00000")
        return lines


    def _get_form_lemma_postag_from_line(self, line):
        wordList = re.sub("[^(\w|·|\-)]", " ",  line).split()
        form = wordList[0]
        lemma = wordList[1]
        postag = wordList[2]
        return form, lemma, postag
