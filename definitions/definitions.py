#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
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

import logging
import xml.etree.ElementTree
import json
import os
from textextract import TextExtract

class Definitions():

    def _get_revision_text(self, revision):
        for child in revision:
            if 'text' in child.tag:
                return child.text

        return ''

    def _get_infinitives(self, filename):
        words = list(line.lower().strip() for line in open(filename))
        return words

    def generate(self, definitions, infinitives = 'data/infinitives.txt', save_dir = 'data'):
        inf = self._get_infinitives(infinitives)
        defs = self._load_definitions_from_xml(definitions, inf)
        self._save_definitions(defs, inf, save_dir)

    # Wiktionary has the definitions with reflexible pronoums (e.g. apoltronar-se)
    # which we need to remove to match our list of infinitive verbs
    def get_without_reflexive_pronoun(self, infinitive):
        SHORT = "'s"
        LONG = "-se"

        if infinitive.endswith(SHORT):
            return infinitive[:-(len(SHORT))]
        elif infinitive.endswith(LONG):
            return infinitive[:-(len(LONG))]

        return infinitive

    def _load_definitions_from_xml(self, filename, infinitives):
        e = xml.etree.ElementTree.parse(filename).getroot()

        definitions = {}
        for page in e:
            is_verb = False
            text = ''
            ca_label = ''

            for page_element in page:
                if 'title' in page_element.tag:
                    ca_label = page_element.text

                if 'revision' in page_element.tag:
                    text = self._get_revision_text(page_element)

                    if text is not None and '{{ca-verb' in text:
                        is_verb = True

            verb = self.get_without_reflexive_pronoun(ca_label.lower().strip())
            if verb not in infinitives:
                logging.debug("Discard not in word list: " + ca_label)
                continue

            if text is None:
                text = ""

            if is_verb is False:
                logging.debug("Discard is not a verb {0} - {1}".format(ca_label, text))
                continue

            textExtract = TextExtract(text)
            ca_desc = textExtract.GetDescription(infinitives)

            if len(ca_desc) == 0:
                logging.debug("Discard no description: " + ca_label)
                continue

            logging.debug("Store {0}-{1}".format(verb, ca_desc))
            definitions[verb] = ca_desc

        return definitions

    def _save_definitions(self, definitions, infinitives, save_dir):

        not_def = 0
        with open(os.path.join(save_dir, "definitions.txt"), "w") as f_definitions:
            for verb in infinitives:
                if verb not in definitions:
                    not_def = not_def + 1
                    logging.debug("No def for: " + verb)
                    continue

                definition = definitions[verb]
                f_definitions.write(verb + '\n')
                f_definitions.write(definition + '\n')


        with open(os.path.join(save_dir, 'definitions.json'), 'w') as outfile:
            json.dump(definitions, outfile)

        print("Definitions: " + str(len(definitions)))
        print("Without Definitions: " + str(not_def))
