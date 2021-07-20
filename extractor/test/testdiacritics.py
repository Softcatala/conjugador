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

from diacritics import Diacritics
import unittest

class TestDiacritics(unittest.TestCase):

    def test_has_diacritic_true(self):
        diacritics = Diacritics()
        diacritics.load_diacritics()

        has = diacritics.has_word_diacritic("vénen")
        self.assertTrue(has)

    def test_has_diacritic_false(self):
        diacritics = Diacritics()
        diacritics.load_diacritics()

        has = diacritics.has_word_diacritic("venen")
        self.assertFalse(has)

if __name__ == '__main__':
    unittest.main()
