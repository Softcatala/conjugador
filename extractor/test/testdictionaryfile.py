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

from dictionaryfile import DictionaryFile
import unittest
from os import path

class TestDictionaryFile(unittest.TestCase):

    def _get_dictionary(self):
        current_dir = path.dirname(path.realpath(__file__))
        filename = path.join(current_dir, "data/diccionari.txt")
        return DictionaryFile(filename)

    def test_get_form_lemma_postag(self):
        FORM = 0
        LEMMA = 1
        POSTAG = 2

        diccionari = self._get_dictionary()
        results = list(diccionari.get_form_lemma_postag())

        self.assertEquals(12, len(results))
        self.assertEquals("dobleguéssim", results[0][FORM])
        self.assertEquals("doblegar", results[0][LEMMA])
        self.assertEquals("VMSI1P02", results[0][POSTAG])

    def test_get_lemmas_for_infinitives(self):
        diccionari = self._get_dictionary()
        lemmas = diccionari.get_lemmas_for_infinitives()

        self.assertEquals(3, len(lemmas))
        self.assertEquals("reconèixer", lemmas[0])
        self.assertEquals("cantar", lemmas[1])
        self.assertEquals("anar_aux", lemmas[2])
        
    def test_exclude_lemmas_list(self):
        diccionari = self._get_dictionary()
        lemmas = set()
        lemmas.add("cantar")
        diccionari.exclude_lemmas_list(lemmas)
        self.assertEquals(11, len(diccionari.lines))

    def test_form_lemma_postag_from_line_specialcases(self):
        diccionari = self._get_dictionary()
        rst = diccionari._get_form_lemma_postag_from_line("col·latària col·latari NCFS000")
        self.assertEquals(('col·latària', 'col·latari', 'NCFS000'), rst)
        rst = diccionari._get_form_lemma_postag_from_line("mont-rogenc mont-rogenc AQ0MS0")
        self.assertEquals(('mont-rogenc', 'mont-rogenc', 'AQ0MS0'), rst)

    def test_valencia(self):
        diccionari = self._get_dictionary()

        self.assertIn(('transmés', 'transmetre', 'VMP00SMV'), diccionari.get_form_lemma_postag())
        self.assertIn(('reconéixer', 'reconèixer', 'VMN0000V'), diccionari.get_form_lemma_postag())

if __name__ == '__main__':
    unittest.main()
