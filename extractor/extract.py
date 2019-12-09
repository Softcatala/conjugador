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
import json
import datetime
import os
import shutil
 
from forms import Forms


def _read_file(input_file):
    with open(input_file) as f:
        return f.readlines()

def _get_inifitives(lines):

    INFINITIVE_DESCRIPTOR = 'VMN00000'

    infinitives = []
    for line in lines:
        wordList = re.sub("[^\w]", " ",  line).split()
        flexionada = wordList[0]
        infinitive = wordList[1]
        descriptor = wordList[2]

        if descriptor != INFINITIVE_DESCRIPTOR:
            continue

        infinitives.append(infinitive)

    return infinitives

def _add_separator(result):
    if len(result) > 0:
        result += " - "

    return result

def _get_variants_imperfet_subjuntiu(result, formes, descriptors, descriptor):

    forma = descriptors.get(descriptor + "1");
    if forma is not None:
        result = _add_separator(result)
        result += '{0} (català central i valencià formal)'.format(forma)
        formes.append(forma)

    forma = descriptors.get(descriptor + "2");
    if forma is not None:
        result = _add_separator(result)
        result += '{0} (català central)'.format(forma)
        formes.append(forma)

    forma = descriptors.get(descriptor + "3");
    if forma is not None:
        result = _add_separator(result)
        result += '{0} (valencià amb -r-)'.format(forma)
        formes.append(forma)

    forma = descriptors.get(descriptor + "4");
    if forma is not None:
        result = _add_separator(result)
        result += '{0} (balear)'.format(forma)
        formes.append(forma)

    forma = descriptors.get(descriptor + "5");
    if forma is not None:
        result = _add_separator(result)
        result += '{0} (valencià formal)'.format(forma)
        formes.append(forma)

    forma = descriptors.get(descriptor + "6");
    if forma is not None:
        result = _add_separator(result)
        result += '{0} (valencià formal)'.format(forma)
        formes.append(forma)

    forma = descriptors.get(descriptor + "7");
    if forma is not None:
        result = _add_separator(result)
        result += '{0} (balear i valencià formal)'.format(forma)
        formes.append(forma)

    return result, formes


def _get_variants(descriptors, descriptor):

    result = ''
    formes = []

    forma = descriptors.get(descriptor + "0");
    if forma is not None:
        result = _add_separator(result)
        result += '{0}'.format(forma)
        formes.append(forma)

    forma = descriptors.get(descriptor + "X");
    if forma is not None:
        result = _add_separator(result)
        result += '{0} (central i valencià)'.format(forma)
        formes.append(forma)

    forma = descriptors.get(descriptor + "Y");
    if forma is not None:
        result = _add_separator(result)
        result += '{0} (central i balear)'.format(forma)
        formes.append(forma)

    forma = descriptors.get(descriptor + "Z");
    if forma is not None:
        result = _add_separator(result)
        result += '{0} (valencià i balear)'.format(forma)
        formes.append(forma)

    forma = descriptors.get(descriptor + "C");
    if forma is not None:
        result = _add_separator(result)
        result += '{0} (central)'.format(forma)
        formes.append(forma)

    forma = descriptors.get(descriptor + "V");
    if forma is not None:
        result = _add_separator(result)
        result += '{0} (valencià)'.format(forma)
        formes.append(forma)

    forma = descriptors.get(descriptor + "B");
    if forma is not None:
        result = _add_separator(result)
        result += '{0} (balear)'.format(forma)
        formes.append(forma)

    return _get_variants_imperfet_subjuntiu(result, formes, descriptors, descriptor)

def _set_plurals_singulars(form, descriptors):

        form.singular1, formes_singular1 = _get_variants(descriptors, form.descriptor + "1S0")
        form.singular2, formes_singular2 = _get_variants(descriptors, form.descriptor + "2S0")
        form.singular3, formes_singular3 = _get_variants(descriptors, form.descriptor + "3S0")

        form.plural1, formes_plural1 = _get_variants(descriptors, form.descriptor + "1P0")
        form.plural2, formes_plural2 = _get_variants(descriptors, form.descriptor + "2P0")
        form.plural3, formes_plural3 = _get_variants(descriptors, form.descriptor + "3P0")

        forms = formes_singular1 + formes_singular2 + formes_singular3 + \
                 formes_plural1 + formes_plural2 + formes_plural3

        form.variants = forms

def _set_plurals_singulars_gerundi(form, descriptors):

        form.singular1, formes_singular1 = _get_variants(descriptors, form.descriptor + "0SM")
        form.singular2, formes_singular2 = _get_variants(descriptors, form.descriptor + "0SF")
        form.singular3, formes_singular3 = _get_variants(descriptors, form.descriptor + "0PM")
        form.plural1, formes_plural1 = _get_variants(descriptors, form.descriptor + "0PF")

        forms = formes_singular1 + formes_singular2 + formes_singular3 + \
                 formes_plural1

        form.variants = forms

def _set_plurals_singulars0(form, descriptors):

        form.singular1, formes_singular1 = _get_variants(descriptors, form.descriptor + "000")

        forms = formes_singular1
        form.variants = forms

def _build_infinitive_descriptors(lines, infinitives):

    inf_desc = {}
    for line in lines:

        wordList = re.sub("[^\w]", " ",  line).split()
        flexionada = wordList[0]
        infinitive = wordList[1]
        descriptor = wordList[2]

        if infinitive in inf_desc:
            descriptors = inf_desc[infinitive]
        else:
            descriptors = {}

        descriptors[descriptor] = flexionada
        inf_desc[infinitive] = descriptors;

    return inf_desc


# Forms' documentation:
# https://freeling-user-manual.readthedocs.io/en/latest/tagsets/tagset-ca/#part-of-speech-verb
def _get_forms(inf_desc, req_infinitive):

    forms = []

    forms.append(Forms('Indicatiu', 'Present', 'VMIP'))
    forms.append(Forms('Indicatiu', 'Futur imperfecte', 'VMIF'))
    forms.append(Forms('Indicatiu', 'Futur hipotètic', 'VMIC'))
    forms.append(Forms('Indicatiu', 'Pretèrit imperfecte', 'VMII'))
    forms.append(Forms('Indicatiu', 'Pretèrit perfecte', 'VMIS'))

    forms.append(Forms('Subjuntiu', 'Present', 'VMSP'))
    forms.append(Forms('Subjuntiu', 'Pretèrit imperfecte', 'VMSI'))
    forms.append(Forms('Subjuntiu', 'Imperatiu', 'VMM0'))
    
    descriptors = inf_desc[req_infinitive]
    for form in forms:
        _set_plurals_singulars(form, descriptors)

    forms.append(Forms('Formes no personals', 'Infinitiu', 'VMN0'))
    forms.append(Forms('Formes no personals', 'Gerundi', 'VMG0'))

    for form in forms[-2:]:
        _set_plurals_singulars0(form, descriptors)

    forms.append(Forms('Formes no personals', 'Participi', 'VMP0'))
    _set_plurals_singulars_gerundi(forms[len(forms) - 1], descriptors)

    return forms

def _serialize_to_file(file_dir, infinitive, forms):
    d = {}
    d[infinitive] = forms
    s = json.dumps(d, default=lambda x: x.__dict__, indent=4)

    with open(os.path.join(file_dir, infinitive + ".json") ,"w") as file:
        file.write(s)

def main():

    input_file = 'catalan-dict-tools/resultats/lt/diccionari.txt'
    output_dir = 'data/jsons/'

    print("Read a dictionary file and extracts the verbs into json files")
    print("Input file: {0}, output dir: {1}".format(input_file, output_dir))
        
    start_time = datetime.datetime.now()

    lines = _read_file(input_file)
    infinitives = _get_inifitives(lines)

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        os.makedirs(output_dir)

    verbs = {}
    inf_desc = _build_infinitive_descriptors(lines, infinitives)

    for infinitive in infinitives:

        #if infinitive != 'cantar':
        #    continue

        file_dir = os.path.join(output_dir, infinitive[:2])
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
            print(file_dir)

        print(infinitive)
        forms = _get_forms(inf_desc, infinitive)
        for form in forms:
            form.print()

        verbs[infinitive] = forms
        _serialize_to_file(file_dir, infinitive, forms)

    print("Number of verbs {0}".format(len(verbs)))
    s = 'Time used for generation: {0}'.format(datetime.datetime.now() - start_time)
    print(s)

if __name__ == "__main__":
    main()
