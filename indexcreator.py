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

import os
import shutil
import json

from whoosh.analysis import StandardAnalyzer
from whoosh.fields import BOOLEAN, TEXT, Schema, STORED, ID
from whoosh.index import create_in
from findfiles import FindFiles


class IndexCreator(object):

    def __init__(self, json_dir):
        self.json_dir = json_dir
        self.dir_name = "indexdir/"
        self.writer = None

    def create(self, in_memory=False):
        analyzer = StandardAnalyzer(minsize=1, stoplist=None)
        schema = Schema(verb_form=TEXT(stored=True, analyzer=analyzer),
                        file_path=STORED)

        if os.path.exists(self.dir_name):
            shutil.rmtree(self.dir_name)

        os.makedirs(self.dir_name)

        ix = create_in(self.dir_name, schema)

        self.writer = ix.writer()
        return ix


    def write_entry(self, verb_form, file_path):

        self.writer.add_document(verb_form = verb_form,
                                 file_path = file_path)

    def _process_file(self, filename):
        with open(filename) as json_file:
            data = json.load(json_file)
            infinitive = list(data.keys())[0]
            print(infinitive)
            print(filename)
            self.write_entry(infinitive, filename)
            

    def process_files(self):
        findFiles = FindFiles()
        files = findFiles.find_recursive(self.json_dir, '*.json')
        for filename in files:
            self._process_file(filename)

        print("Processed {0} files".format(len(files)))


