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

import json
from findfiles import FindFiles
from search import Search
from autocomplete import Autocomplete
from indexletter import IndexLetter

class IndexCreator(object):

    def __init__(self, json_dir):
        self.json_dir = json_dir
        self.index_letters = 0
        self.search = Search()
        self.autocomplete = Autocomplete()
        self.indexletter = IndexLetter()

    def create(self):
        self.search.create()
        self.autocomplete.create()
        self.indexletter.create()


    def _write_entry(self, indexed, verb_form, file_path, is_infinitive, infinitive, mode, tense, title):

        self.search.write_entry(verb_form, file_path, is_infinitive, infinitive, mode, tense, title)
        self.autocomplete.write_entry(verb_form, file_path, is_infinitive, infinitive, mode, tense, title)
        self.indexletter.write_entry(verb_form, is_infinitive, infinitive, title)

#        print(verb_form)
#        print(mode)
#        print(tense)
#        print("---")
        indexed.add(verb_form)

    def _get_title(self, forms):
        for form in forms:
            title = form['title']
            if title:
                return title

        raise Exception("No title found for the entry")


    def _process_file(self, filename):
        with open(filename) as json_file:
            data = json.load(json_file)
            infinitive = list(data.keys())[0]
            
            #if infinitive != 'cantar':
            #    return 0

            indexed = set()
            title = self._get_title(data[infinitive])

            infinitive_found = False
            for form in data[infinitive]:
                if 'definition_credits' in form:
                    continue

                sps = ['singular1', 'singular2', 'singular3', 'plural1', 'plural2', 'plural3']
                for sp in sps:
                    for conjugacio in form[sp]:
                        word = conjugacio['word']

                        if word in indexed:
                            continue

                        words = [x.strip() for x in word.split('/')]
                        for word in words:
                            is_infinitive = form['tense'] == "Infinitiu"
                            if is_infinitive:
                                infinitive_found = True

                            self._write_entry(indexed, word, filename, is_infinitive, infinitive, form['mode'], form['tense'], title)

            # This is the case of anar (auxiliar)
            if infinitive_found is False:
                self._write_entry(indexed, infinitive, filename, True, infinitive, 'Formes no personals', 'Infinitiu', title)
                   
        return len(indexed)

    def _save_index(self):
        self.search.save()
        self.autocomplete.save()
        self.indexletter.save()

    def process_files(self):
        findFiles = FindFiles()
        files = findFiles.find_recursive(self.json_dir, '*.json')
        indexed = 0
        for filename in files:
            indexed += self._process_file(filename)

        self._save_index()
        print("Processed {0} files, indexed {1} variants, indexed letters {2}, indexed autocomplete entries {3}".
              format(len(files), indexed, self.indexletter.entries, self.autocomplete.doc_count()))
