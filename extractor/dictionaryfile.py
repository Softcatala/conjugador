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
        self.lines = self._read_file(filename)
        self._valencia()
        self._pre_process_anar_auxiliar()

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

    def exclude_lemmas_list(self, lemmas):
        size = len(self.lines)
        for idx in range(size - 1, 0, -1):
            line = self.lines[idx]
            form, lemma, postag = self._get_form_lemma_postag_from_line(line)
            lemma = lemma.lower()
            if lemma in lemmas:
                self.lines.remove(line)

        print(f"Removed {size - len(self.lines)} lemmas from dictionary")
        
    def _load_specific_lemmas_with_pos(self, tag):
        lemmas = {}
        for i in range(0, len(self.lines)):
            line = self.lines[i]
            form, lemma, postag = self._get_form_lemma_postag_from_line(line)
            if postag == tag:
                lemmas.setdefault(lemma, []).append((i, form))

        return lemmas

    '''
        El diccionari d'on llegim les dades no té etiquetades correctament algunes formes com a valencianes.
        Esmenar-ho no es pot fer a curt plaç, ja que té implicacions en altres eines. Com a solució, marquem
        aquí de forma dinàmica aquestes formes com a valencianes.
    '''

    def _valencia(self):
        self._valencia_form("VMP00SM0", "ès", "és", )
        self._valencia_form("VMN00000", "èixer", "éixer")

    # Transforms a tag VMN00000 into VMN0000V
    def _valencia_update_tag_in_line(self, line_idx, tag):
        line = self.lines[line_idx]
        idx = line.find(tag)
        val_tag = tag[0:-1] + "V"
        line = line.replace(tag, val_tag)
        self.lines[line_idx] = line

    def _valencia_form(self, tag, central, valencia):
        lemmas = self._load_specific_lemmas_with_pos(tag)
        total = 0

        for forms in (forms for forms in lemmas.values() if len(forms) > 1):
            found_ca = any(form.endswith(central) for i, form in forms)
            index_va = next((i for i, form in forms if form.endswith(valencia)), None)
        
            if found_ca and index_va:
                self._valencia_update_tag_in_line(index_va, tag)
                total += 1

        print(f"Marked {total} forms tagged {tag} as Valencian")
            
    def _read_file(self, input_file):
        with open(input_file) as f:
            return f.readlines()

    '''
        La forma en infinitiu "anar" no és una forma auxiliar i no apareix com a infinitiu al diccionari.
        Com a resultat totes les formes vaja, vam, van queden penjades sense mostrar-se.
    '''
    def _pre_process_anar_auxiliar(self):
        for i in range(0, len(self.lines)):
            line = self.lines[i]
            form, lemma, postag = self._get_form_lemma_postag_from_line(line)

            if lemma =='anar' and postag[0:2] == 'VA':
                line = f'{form} anar_aux {postag}'
                self.lines[i] = line

        self.lines.append("anar anar_aux VAN00000")


    def _get_form_lemma_postag_from_line(self, line):
        wordList = re.sub(r"[^(\w|·|\-)]", " ",  line).split()
        form = wordList[0]
        lemma = wordList[1]
        postag = wordList[2]
        return form, lemma, postag
