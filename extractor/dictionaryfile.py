#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019-2022 Jordi Mas i Hernandez <jmas@softcatala.org>
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


import re
from pathlib import Path
from typing import Iterator


class DictionaryFile:
    """
    Reads a dictionary text file with entries with the following format:
    - form lemma postag
    - cantaria cantar VMIC1S00

    Makes the data accessible in the form of: form, lemma and postag.

    Args:
        file_path (str): The path of the file to read.
    """

    def __init__(self, file_path: str) -> None:
        """
        Initializes the DictionaryFile with a given file name.

        Args:
            file_path (str): The path of the file to read.
        """
        self.lines = self._read_file(file_path)
        self._valencia()
        self._pre_process_anar_auxiliar()

    def get_form_lemma_postag(self) -> Iterator[tuple[str, str, str]]:
        """
        Gets all the forms, lemmas and postags for each entry in the dictionary
        in an iterator.

        Yields:
            tuple[str, str ,str]: A tuple containing the form, lemma and postag.
        """
        for line in self.lines:
            form, lemma, postag = self._get_form_lemma_postag_from_line(line)
            yield form, lemma, postag

    def get_lemmas_for_infinitives(self) -> list[str]:
        """
        Gets all the lemmas for the infinitive variants (VMN00000, VAN00000, VSN00000).

        Returns:
            list[str]: A list of all the lemmas of all the infinitives in the dictionary.
        """
        INFINITIVE_DESCRIPTORS = {"VMN00000", "VAN00000", "VSN00000"}

        lemmas = []
        for line in self.lines:
            form, lemma, postag = self._get_form_lemma_postag_from_line(line)

            if postag not in INFINITIVE_DESCRIPTORS:
                continue

            lemmas.append(lemma)

        return lemmas

    def exclude_lemmas_list(self, lemmas: list[str]) -> None:
        """
        Excludes a given list of lemmas from the dictionary.

        Args:
            lemmas (list[str]): The list of lemmas to exclude.
        """
        size = len(self.lines)
        for idx in range(size - 1, -1, -1):
            line = self.lines[idx]
            form, lemma, postag = self._get_form_lemma_postag_from_line(line)
            lemma = lemma.lower()
            if lemma in lemmas:
                self.lines.remove(line)

        print(f"Removed {size - len(self.lines)} lemmas from dictionary")

    def _load_specific_lemmas_with_pos(
        self, tag: str
    ) -> dict[str, list[tuple[int, str]]]:
        lemmas = {}
        for i in range(len(self.lines)):
            line = self.lines[i]
            form, lemma, postag = self._get_form_lemma_postag_from_line(line)
            if postag == tag:
                lemmas.setdefault(lemma, []).append((i, form))

        return lemmas

    def _valencia(self) -> None:
        # El diccionari d'on llegim les dades no té etiquetades correctament algunes formes com a valencianes.
        # Esmenar-ho no es pot fer a curt plaç, ja que té implicacions en altres eines. Com a solució, marquem
        # aquí de forma dinàmica aquestes formes com a valencianes.
        self._valencia_form(
            "VMP00SM0",
            "ès",
            "és",
        )
        self._valencia_form("VMN00000", "èixer", "éixer")

    def _valencia_update_tag_in_line(self, line_idx: int, tag: str) -> None:
        """
        Transforms a tag VMN00000 into VMN0000V

        Args:
            line_idx (int): The line index to update.
            tag (str): The tag value you want to replace the original for.
        """
        line = self.lines[line_idx]
        val_tag = tag[0:-1] + "V"
        line = line.replace(tag, val_tag)
        self.lines[line_idx] = line

    def _valencia_form(self, tag: str, central: str, valencia: str) -> None:
        lemmas = self._load_specific_lemmas_with_pos(tag)
        total = 0

        for forms in (forms for forms in lemmas.values() if len(forms) > 1):
            found_ca = any(form.endswith(central) for i, form in forms)
            index_va = next(
                (i for i, form in forms if form.endswith(valencia)), None
            )

            if found_ca and index_va:
                self._valencia_update_tag_in_line(index_va, tag)
                total += 1

        print(f"Marked {total} forms tagged {tag} as Valencian")

    def _read_file(self, input_file: str) -> list[str]:
        with Path(input_file).open() as f:
            return f.readlines()

    def _pre_process_anar_auxiliar(self) -> None:
        # La forma en infinitiu "anar" no és una forma auxiliar i no apareix com
        # a infinitiu al diccionari.
        # Com a resultat, totes les formes vaja, vam, van queden penjades sense mostrar-se.
        for i in range(len(self.lines)):
            line = self.lines[i]
            form, lemma, postag = self._get_form_lemma_postag_from_line(line)

            if lemma == "anar" and postag[0:2] == "VA":
                line = f"{form} anar_aux {postag}"
                self.lines[i] = line

        self.lines.append("anar anar_aux VAN00000")

    def _get_form_lemma_postag_from_line(
        self, line: str
    ) -> tuple[str, str, str]:
        wordList = re.sub(r"[^(\w|·|\-)]", " ", line).split()
        form = wordList[0]
        lemma = wordList[1]
        postag = wordList[2]
        return form, lemma, postag
