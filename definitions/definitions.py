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

import json
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.etree.ElementTree import Element

from definitions.textextract import TextExtract


class Definitions:
    """
    Generates a dictionary of the definitions of all the verbs in catalan and saves it
    by default at `data/definitions.txt`.
    """

    def _get_revision_text(self, revision: Element) -> str:
        for child in revision:
            if "text" in child.tag:
                return child.text if child.text else ""

        return ""

    def _get_infinitives(self, filename: str) -> list[str]:
        words = [
            line.lower().strip()
            for line in Path(filename).read_text().splitlines()
        ]
        return words

    def generate(
        self,
        definitions_path: str,
        infinitives_path: str = "data/infinitives.txt",
        save_dir: str = "data",
    ) -> None:
        """
        Generates a dictionary of the definitions of all the verbs in a file by loading
        them along with their definitions from a different XML file. Saves them into
        a `definitions.txt` file in the specified save directory.

        Args:
            definitions_path (str): The path of the XML file containing the definitions.
            infinitives_path (str): The path to the file containing the infinitives you want defs of.
            save_dir (str): The directory where the resulting `definitions.txt` file will be saved.
        """
        inf = self._get_infinitives(infinitives_path)
        defs = self._load_definitions_from_xml(definitions_path, inf)
        self._save_definitions(defs, inf, save_dir)

    def get_without_reflexive_pronoun(self, infinitive: str) -> str:
        """
        Returns the infinitive without the reflexive pronouns.
        This is because Wiktionary has the definitions with reflexible pronoums
        which we need to remove to match our list of infinitive verbs.

        E.g. apoltronar-se -> apoltronar.

        Args:
            infinitive (str): The infinitive from which to strip the reflexive pronouns.

        Returns:
            str: The infinitive without the reflexive pronouns.
        """
        SHORT = "'s"
        LONG = "-se"

        if infinitive.endswith(SHORT):
            return infinitive[: -(len(SHORT))]
        if infinitive.endswith(LONG):
            return infinitive[: -(len(LONG))]

        return infinitive

    def _load_definitions_from_xml(
        self, file_path: str, infinitives: list[str]
    ) -> dict:
        e = ET.parse(file_path).getroot()

        definitions = {}
        for page in e:
            is_verb = False
            text = ""
            ca_label = ""

            for page_element in page:
                if "title" in page_element.tag:
                    ca_label = (
                        page_element.text
                        if page_element.text is not None
                        else ""
                    )

                if "revision" in page_element.tag:
                    text = self._get_revision_text(page_element)

                    if text is not None and "{{ca-verb" in text:
                        is_verb = True

            verb = self.get_without_reflexive_pronoun(ca_label.lower().strip())
            if verb not in infinitives:
                logging.debug(f"Discard not in word list: {ca_label}")
                continue

            if text is None:
                text = ""

            if is_verb is False:
                logging.debug(
                    "Discard is not a verb {0} - {1}".format(ca_label, text)
                )
                continue

            textExtract = TextExtract(text)
            ca_desc = textExtract.get_description(infinitives)

            if len(ca_desc) == 0:
                logging.debug(f"Discard no description: {ca_label}")
                continue

            logging.debug(f"Store {verb}-{ca_desc}")
            definitions[verb] = ca_desc

        return definitions

    def _save_definitions(
        self, definitions: dict, infinitives: list[str], save_dir: str
    ) -> None:
        not_def = 0
        definitions_path = Path(save_dir) / "definitions.txt"
        with definitions_path.open("w") as f_definitions:
            for verb in infinitives:
                if verb not in definitions:
                    not_def = not_def + 1
                    logging.debug("No def for: " + verb)
                    continue

                definition = definitions[verb]
                f_definitions.write(verb + "\n")
                f_definitions.write(definition + "\n")

        file_path = Path(save_dir) / "definitions.json"
        with file_path.open("w") as outfile:
            json.dump(definitions, outfile)

        print("Definitions: " + str(len(definitions)))
        print("Without Definitions: " + str(not_def))
