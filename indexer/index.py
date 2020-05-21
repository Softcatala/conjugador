# -*- encoding: utf-8 -*-
#
# Copyright (c) 2019 Jordi Mas i Hernandez <jmas@softcatala.org>
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

from whoosh.util.text import rcompile
from whoosh.analysis import StandardAnalyzer
import os
import shutil

class Index(object):

    def __init__(self):
        self.tokenizer_pattern = rcompile(r"(\w|·)+(\.?(\w|·)+)*") # Includes l·l
        self.analyzer = StandardAnalyzer(minsize=1, stoplist=None, expression=self.tokenizer_pattern)

    def _create_dir(self, directory):
        if os.path.exists(directory):
            shutil.rmtree(directory)

        os.makedirs(directory)

    def _verbs_to_ignore_in_autocomplete(self, mode, tense):
        if mode == 'Indicatiu':
            if any(t in tense for t in ["Perfet", "Plusquamperfet", "Passat perifràstic",\
                                        "Passat anterior", "Passat anterior perifràstic",\
                                        "Futur perfet", "Condicional perfet"]):
                return True

        if mode == 'Subjuntiu':
            if any(t in tense for t in ["Perfet", "Plusquamperfet"]):
                return True

        if mode == 'Formes no personals':
            if any(t in tense for t in ["Infinitiu compost", "Gerundi compost"]):
                return True

        return False
