#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

import re

class Forms:

    def __init__(self, group, form):
        self.group = group
        self.form = form
        self.singular1 = '-' 
        self.singular2 = '-'
        self.singular3 = '-'
        self.plural1 = '-'
        self.plural2 = '-'
        self.plural3 = '-'

    def print(self):
        print("---")
        print("* {0} ({1})".format(self.form,  self.group))
        print(self.singular1)
        print(self.singular2)
        print(self.singular3)
        print(self.plural1)
        print(self.plural2)
        print(self.plural3)

def _read_file():
    with open('diccionari.txt') as f:
        return f.readlines()

def _get_inifitives(lines):

    infinitives = []
    for line in lines:
        wordList = re.sub("[^\w]", " ",  line).split()
        flexionada = wordList[0]
        infinitive = wordList[1]
        descriptor = wordList[2]

        if descriptor != 'VMN00000':
            continue

        infinitives.append(infinitive)

    return infinitives

def _add_separator(result):
    if len(result) > 0:
        result += " - "

    return result

def _get_variants(descriptors, descriptor):

        result = ''

        forma = descriptors.get(descriptor + "0");
        if forma is not None:
            result = _add_separator(result)
            result += '{0}'.format(forma)

        forma = descriptors.get(descriptor + "X");
        if forma is not None:
            result = _add_separator(result)
            result += '{0} (central i valencià)'.format(forma)

        forma = descriptors.get(descriptor + "Y");
        if forma is not None:
            result = _add_separator(result)
            result += '{0} (central i balear)'.format(forma)

        forma = descriptors.get(descriptor + "Z");
        if forma is not None:
            result = _add_separator(result)
            result += '{0} (valencià i balear)'.format(forma)

        forma = descriptors.get(descriptor + "C");
        if forma is not None:
            result = _add_separator(result)
            result += '{0} (central)'.format(forma)

        forma = descriptors.get(descriptor + "V");
        if forma is not None:
            result = _add_separator(result)
            result += '{0} (valencià)'.format(forma)

        forma = descriptors.get(descriptor + "B");
        if forma is not None:
            result = _add_separator(result)
            result += '{0} (balear)'.format(forma)
        
        return result

def _set_plurals_singulars(form, descriptor, descriptors):

        form.singular1 = _get_variants(descriptors, descriptor + "1S0")
        form.singular2 = _get_variants(descriptors, descriptor + "2S0")
        form.singular3 = _get_variants(descriptors, descriptor + "3S0")

        form.plural1 = _get_variants(descriptors, descriptor + "1P0")
        form.plural2 = _get_variants(descriptors, descriptor + "2P0")
        form.plural3 = _get_variants(descriptors, descriptor + "3P0")


# Forms' documentation:
# https://freeling-user-manual.readthedocs.io/en/latest/tagsets/tagset-ca/#part-of-speech-verb
def _get_forms(req_inifitive, lines):

    forms = []

    VMII = Forms('Indicatiu', 'Pretèrit imperfecte')
    VMSP = Forms('Subjuntiu', 'Present')
    VMIP = Forms('Indicatiu', 'Present')
    
    descriptors = {}
    for line in lines:
        wordList = re.sub("[^\w]", " ",  line).split()
        flexionada = wordList[0]
        infinitive = wordList[1]
        descriptor = wordList[2]

        if infinitive != req_inifitive:
            continue

        descriptors[descriptor] = flexionada

    _set_plurals_singulars(VMII, 'VMII', descriptors)
    _set_plurals_singulars(VMSP, 'VMSP', descriptors)
    _set_plurals_singulars(VMIP, 'VMIP', descriptors)


    forms.append(VMII)
    forms.append(VMSP)
    forms.append(VMIP)
    return forms

def main():

    lines = _read_file()
    infinitives = _get_inifitives(lines)

    for infinitive in infinitives:
        if infinitive != 'cantar':
            continue

        print(infinitive)
        forms = _get_forms(infinitive, lines)
        for form in forms:
            form.print()
            

if __name__ == "__main__":
    main()
