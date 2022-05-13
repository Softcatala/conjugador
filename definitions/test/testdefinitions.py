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

import unittest
import tempfile
import os
import hashlib

from definitions import Definitions

class TestDefinitions(unittest.TestCase):

    def _hash_file(self, filename):
        BUF_SIZE = 65536
        sha1 = hashlib.sha1()

        with open(filename, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha1.update(data)

        return sha1.hexdigest()

    def test_get_without_reflexive_pronoun(self):
        definitions = Definitions()
        self.assertEquals("apoltronar", definitions.get_without_reflexive_pronoun("apoltronar-se"))
        self.assertEquals("entrebatre", definitions.get_without_reflexive_pronoun("entrebatre's"))
        self.assertEquals("cantar", definitions.get_without_reflexive_pronoun("cantar"))

    def test_generate(self):

        with tempfile.TemporaryDirectory() as dirpath:
            definitions = Definitions()
            definitions.generate("test/data/definitions.xml", infinitives = 'test/data/infinitives.txt', save_dir = dirpath)

            def_gen = self._hash_file(os.path.join(dirpath, "definitions.txt"))
            def_ref = self._hash_file("test/data/definitions.txt")
            defj_gen = self._hash_file(os.path.join(dirpath, "definitions.json"))
            defj_ref = self._hash_file("test/data/definitions.json")

        self.assertEquals(def_ref, def_gen)
        self.assertEquals(defj_ref, defj_gen)



if __name__ == '__main__':
    unittest.main()
