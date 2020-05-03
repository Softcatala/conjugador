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
from whoosh.util.text import rcompile
from whoosh.analysis import StandardAnalyzer
from whoosh.fields import TEXT, Schema
from whoosh.index import create_in
from findfiles import FindFiles
from whoosh.analysis import CharsetFilter
from whoosh.support.charset import accent_map

class IndexCreator(object):

    def __init__(self, json_dir):
        self.json_dir = json_dir
        self.dir_name_search = "data/search_index/"
        self.dir_name_autocomplete = "data/autocomplete_index/"
        self.dir_name_indexletter = "data/indexletter_index/"
        self.writer = None
        self.writer_autocomplete = None
        self.writer_indexletter = None
        self.tokenizer_pattern = rcompile(r"(\w|·)+(\.?(\w|·)+)*") # Includes l·l
        self.analyzer = StandardAnalyzer(minsize=1, stoplist=None, expression=self.tokenizer_pattern)
        self.index_letters = 0


    def _create_dir(self, directory):
        if os.path.exists(directory):
            shutil.rmtree(directory)

        os.makedirs(directory)

    def create(self):
        self._create_search()
        self._create_autocomplete()
        self._create_indexletter()

    def _create_search(self):
        analyzer_no_diatritics = self.analyzer | CharsetFilter(accent_map)
        schema = Schema(verb_form=TEXT(stored=True, sortable=True, analyzer=self.analyzer),
                        verb_form_no_diacritics=TEXT(analyzer=analyzer_no_diatritics),
                        index_letter=TEXT(sortable=True, analyzer=self.analyzer),
                        file_path=TEXT(stored=True, sortable=True))

        self._create_dir(self.dir_name_search)
        ix = create_in(self.dir_name_search, schema)
        self.writer = ix.writer()

    def _create_autocomplete(self):
        schema = Schema(verb_form=TEXT(stored=True, sortable=True, analyzer=self.analyzer),
                        infinitive=TEXT(stored=True, analyzer=self.analyzer),
                        autocomplete_sorting=TEXT(sortable=True))

        self._create_dir(self.dir_name_autocomplete)
        ix = create_in(self.dir_name_autocomplete, schema)
        self.writer_autocomplete = ix.writer()

    def _create_indexletter(self):
        schema = Schema(verb_form=TEXT(stored=True, sortable=True, analyzer=self.analyzer),
                        index_letter=TEXT(sortable=True, analyzer=self.analyzer))

        self._create_dir(self.dir_name_indexletter)
        ix = create_in(self.dir_name_indexletter, schema)
        self.writer_indexletter = ix.writer()

    def _get_first_letter_for_index(self, word_ca):
        s = ''
        if word_ca is None:
            return s

        s = word_ca[0].lower()
        mapping = { u'à' : u'a',
                    u'è' : u'e',
                    u'é' : u'e',
                    u'í' : u'i',
                    u'ó' : u'o',
                    u'ò' : u'o',
                    u'ú' : u'u'}

        if s in mapping:
            s = mapping[s]

        return s

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


    def _write_entry(self, indexed, verb_form, file_path, is_infinitive, infinitive, mode, tense):

        if is_infinitive:
            index_letter = self._get_first_letter_for_index(verb_form)
        else:
            index_letter = None

        autocomplete_sorting = self.get_autocomple_sorting_key(verb_form, is_infinitive, infinitive)

        self.writer.add_document(verb_form = verb_form,
                                 verb_form_no_diacritics = verb_form,
                                 file_path = file_path,
                                 index_letter = index_letter)

        if not self._verbs_to_ignore_in_autocomplete(mode, tense):
            self.writer_autocomplete.add_document(verb_form = verb_form,
                                                  infinitive = infinitive,
                                                  autocomplete_sorting = autocomplete_sorting)

        if index_letter is not None:
            self.index_letters = self.index_letters +1
            self.writer_indexletter.add_document(verb_form = verb_form,
                                     index_letter = index_letter)

        #print(word)
        #print(form)
        #print("---")
        indexed.add(verb_form)

    def _process_file(self, filename):
        with open(filename) as json_file:
            data = json.load(json_file)
            infinitive = list(data.keys())[0]
            
            #if infinitive != 'cantar':
            #    return 0

            indexed = set()

            for form in data[infinitive]:
                sps = ['singular1', 'singular2', 'singular3', 'plural1', 'plural2', 'plural3']
                for sp in sps:
                    for conjugacio in form[sp]:
                        word = conjugacio['word']
                        postag = form['postag']

                        if word in indexed:
                            continue

                        words = [x.strip() for x in word.split('/')]
                        for word in words:
                            is_infinitive = form['tense'] == "Infinitiu"
                            #self._write_entry(indexed, word, form['tense'], is_infinitive, infinitive, postag, mode)
                            self._write_entry(indexed, word, filename, is_infinitive, infinitive, form['mode'], form['tense'])
                   
        return len(indexed)

    def save_index(self):
        self.writer.commit()
        self.writer_autocomplete.commit()
        self.writer_indexletter.commit()


    def process_files(self):
        findFiles = FindFiles()
        files = findFiles.find_recursive(self.json_dir, '*.json')
        indexed = 0
        for filename in files:
            indexed += self._process_file(filename)

        print("Processed {0} files, indexed {1} variants, index letters {2}".
              format(len(files), indexed, self.index_letters))

    def get_autocomple_sorting_key(self, verb_form, is_infinitive, infinitive):
        SORTING_PREFIX='_'
        if is_infinitive:
            # By starting with '_', it forces infinitives to appear first in search
            return f'{SORTING_PREFIX}{infinitive}'
        else:
            return f'{verb_form}{SORTING_PREFIX}{infinitive}'
