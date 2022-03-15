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

from reflexius import Reflexius
import unittest

class TestReflexius(unittest.TestCase):

    def setUp(self):
        self.reflexius = Reflexius()
        self.reflexius.load_reflexius()

    def test_has_reflexiu_no(self):
        reflexiu = self.reflexius.get_reflexiu("cantar")
        self.assertEquals("cantar", reflexiu)

    def _test_get_reflexiu_yes(self):
        reflexiu = self.reflexius.get_reflexiu("abromar")
        self.assertEquals("abromar-se", reflexiu)

    def _test_get_reflexiu_auto_yes(self):
        reflexiu = self.reflexius.get_reflexiu("autocensurar")
        self.assertEquals("autocensurar-se", reflexiu)

    def _test_get_reflexiu_yes_aprof(self):
        reflexiu = self.reflexius.get_reflexiu("condoldre")
        self.assertEquals("condoldre's", reflexiu)


if __name__ == '__main__':
    unittest.main()
