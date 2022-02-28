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

    def test_get_form_lemma_postag(self):
        FORM = 0
        LEMMA = 1
        POSTAG = 2

        current_dir = path.dirname(path.realpath(__file__))
        filename = path.join(current_dir, "data/diccionari.txt")
        diccionari = DictionaryFile(filename)
        results = list(diccionari.get_form_lemma_postag())

        self.assertEquals(8, len(results))
        self.assertEquals("dobleguéssim", results[0][FORM])
        self.assertEquals("doblegar", results[0][LEMMA])
        self.assertEquals("VMSI1P02", results[0][POSTAG])

    def test_get_lemmas_for_infinitives(self):
        current_dir = path.dirname(path.realpath(__file__))
        filename = path.join(current_dir, "data/diccionari.txt")
        diccionari = DictionaryFile(filename)
        lemmas = diccionari.get_lemmas_for_infinitives()

        self.assertEquals(2, len(lemmas))
        self.assertEquals("cantar", lemmas[0])
        self.assertEquals("anar_aux", lemmas[1])

if __name__ == '__main__':
    unittest.main()
