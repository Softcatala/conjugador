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
from forms import Form


def _read_file(input_file):
    with open(input_file) as f:
        return f.readlines()

def _get_inifitives(lines):

    INFINITIVE_DESCRIPTORS = set(['VMN00000', 'VAN00000', 'VSN00000'])

    infinitives = []
    for line in lines:
        wordList = re.sub("[^(\w|·)]", " ",  line).split()
        flexionada = wordList[0]
        infinitive = wordList[1]
        descriptor = wordList[2]

        if descriptor not in INFINITIVE_DESCRIPTORS:
            continue

        infinitives.append(infinitive)

    return infinitives

def _add_separator(result):
    if len(result) > 0:
        result += " - "

    return result

def _get_variants(descriptors, descriptor, prefix=''):

    result = []

    variants = ["0", "1", "2", "3", "4", "5", "6", "7", "C", "X", "Y", "Z", "V", "B"]

    for variant in variants:
        forma = descriptors.get(descriptor + variant);
        if forma is not None:
            result.append(Form(forma, variant, prefix))

    return result

def _get_verb_mode(postag):
    return postag[2]

def _set_plurals_singulars(form, descriptors):
    if _get_verb_mode(form.descriptor) not in ['I', 'S', 'M']:
        return
    form.singular1 = _get_variants(descriptors, form.descriptor + "1S0")
    form.singular2 = _get_variants(descriptors, form.descriptor + "2S0")
    form.singular3 = _get_variants(descriptors, form.descriptor + "3S0")

    form.plural1 = _get_variants(descriptors, form.descriptor + "1P0")
    form.plural2 = _get_variants(descriptors, form.descriptor + "2P0")
    form.plural3 = _get_variants(descriptors, form.descriptor + "3P0")

def _set_plurals_singulars_participi(form, descriptors):
    if _get_verb_mode(form.descriptor) != 'P':
        return
    form.singular1 = _get_variants(descriptors, form.descriptor + "0SM")
    form.singular2 = _get_variants(descriptors, form.descriptor + "0SF")
    form.singular3 = _get_variants(descriptors, form.descriptor + "0PM")
    form.plural1 = _get_variants(descriptors, form.descriptor + "0PF")


def _set_plurals_singulars0(form, descriptors):
    form.singular1 = _get_variants(descriptors, form.descriptor + "000")

def _set_infinitiu_compost(form, descriptors):
    if _get_verb_mode(form.descriptor) != 'P':
        return
    form.singular1 = _get_variants(descriptors, form.descriptor + "0SM", "haver ")

def _set_gerundi_compost(form, descriptors):
    if _get_verb_mode(form.descriptor) != 'P':
        return
    form.singular1 = _get_variants(descriptors, form.descriptor + "0SM", "havent ")

def _set_perfet_indicatiu(form, descriptors):
    if _get_verb_mode(form.descriptor) != 'P':
        return
    form.singular1 = _get_variants(descriptors, form.descriptor + "0SM", "he ")
    form.singular2 = _get_variants(descriptors, form.descriptor + "0SM", "has ")
    form.singular3 = _get_variants(descriptors, form.descriptor + "0SM", "ha ")

    form.plural1 = _get_variants(descriptors, form.descriptor + "0SM", "hem ")
    form.plural2 = _get_variants(descriptors, form.descriptor + "0SM", "heu ")
    form.plural3 = _get_variants(descriptors, form.descriptor + "0SM", "han ")

def _set_plusquamperfet_indicatiu(form, descriptors):
    if _get_verb_mode(form.descriptor) != 'P':
        return
    form.singular1 = _get_variants(descriptors, form.descriptor + "0SM", "havia ")
    form.singular2 = _get_variants(descriptors, form.descriptor + "0SM", "havies ")
    form.singular3 = _get_variants(descriptors, form.descriptor + "0SM", "havia ")

    form.plural1 = _get_variants(descriptors, form.descriptor + "0SM", "havíem ")
    form.plural2 = _get_variants(descriptors, form.descriptor + "0SM", "havíeu ")
    form.plural3 = _get_variants(descriptors, form.descriptor + "0SM", "havin ")

def _set_passatperifrastic_indicatiu(form, descriptors):
    if _get_verb_mode(form.descriptor) != 'N':
        return
    form.singular1 = _get_variants(descriptors, form.descriptor + "000", "vaig ")
    form.singular2 = _get_variants(descriptors, form.descriptor + "000", "vas (vares) ")
    form.singular3 = _get_variants(descriptors, form.descriptor + "000", "va ")

    form.plural1 = _get_variants(descriptors, form.descriptor + "000", "vam (vàrem) ")
    form.plural2 = _get_variants(descriptors, form.descriptor + "000", "vau (vàreu) ")
    form.plural3 = _get_variants(descriptors, form.descriptor + "000", "van (varen) ")

def _set_passatanterior_indicatiu(form, descriptors):
    if _get_verb_mode(form.descriptor) != 'P':
        return
    form.singular1 = _get_variants(descriptors, form.descriptor + "0SM", "haguí ")
    form.singular2 = _get_variants(descriptors, form.descriptor + "0SM", "hagueres ")
    form.singular3 = _get_variants(descriptors, form.descriptor + "0SM", "hagué ")

    form.plural1 = _get_variants(descriptors, form.descriptor + "0SM", "haguérem ")
    form.plural2 = _get_variants(descriptors, form.descriptor + "0SM", "haguéreu ")
    form.plural3 = _get_variants(descriptors, form.descriptor + "0SM", "hagueren ")

def _set_passatanteriorperifrastic_indicatiu(form, descriptors):
    if _get_verb_mode(form.descriptor) != 'P':
        return
    form.singular1 = _get_variants(descriptors, form.descriptor + "0SM", "vaig haver ")
    form.singular2 = _get_variants(descriptors, form.descriptor + "0SM", "vas haver ")
    form.singular3 = _get_variants(descriptors, form.descriptor + "0SM", "va haver ")

    form.plural1 = _get_variants(descriptors, form.descriptor + "0SM", "vam haver ")
    form.plural2 = _get_variants(descriptors, form.descriptor + "0SM", "vau haver ")
    form.plural3 = _get_variants(descriptors, form.descriptor + "0SM", "van haver ")

def _set_futurperfet_indicatiu(form, descriptors):
    if _get_verb_mode(form.descriptor) != 'P':
        return
    form.singular1 = _get_variants(descriptors, form.descriptor + "0SM", "hauré ")
    form.singular2 = _get_variants(descriptors, form.descriptor + "0SM", "hauràs ")
    form.singular3 = _get_variants(descriptors, form.descriptor + "0SM", "haurà ")

    form.plural1 = _get_variants(descriptors, form.descriptor + "0SM", "haurem ")
    form.plural2 = _get_variants(descriptors, form.descriptor + "0SM", "haureu ")
    form.plural3 = _get_variants(descriptors, form.descriptor + "0SM", "hauran ")

def _set_condicionalperfet_indicatiu(form, descriptors):
    if _get_verb_mode(form.descriptor) != 'P':
        return
    form.singular1 = _get_variants(descriptors, form.descriptor + "0SM", "hauria ")
    form.singular2 = _get_variants(descriptors, form.descriptor + "0SM", "hauries ")
    form.singular3 = _get_variants(descriptors, form.descriptor + "0SM", "hauria ")

    form.plural1 = _get_variants(descriptors, form.descriptor + "0SM", "hauríem ")
    form.plural2 = _get_variants(descriptors, form.descriptor + "0SM", "hauríeu ")
    form.plural3 = _get_variants(descriptors, form.descriptor + "0SM", "haurien ")

def _set_perfet_subjuntiu(form, descriptors):
    if _get_verb_mode(form.descriptor) != 'P':
        return
    form.singular1 = _get_variants(descriptors, form.descriptor + "0SM", "hagi / haja ")
    form.singular2 = _get_variants(descriptors, form.descriptor + "0SM", "hagis / hages ")
    form.singular3 = _get_variants(descriptors, form.descriptor + "0SM", "hagi / haja ")

    form.plural1 = _get_variants(descriptors, form.descriptor + "0SM", "hàgim / hàgem ")
    form.plural2 = _get_variants(descriptors, form.descriptor + "0SM", "hàgiu / hàgeu ")
    form.plural3 = _get_variants(descriptors, form.descriptor + "0SM", "hagin / hagen ")

def _set_plusquamperfet_subjuntiu(form, descriptors):
    if _get_verb_mode(form.descriptor) != 'P':
        return
    form.singular1 = _get_variants(descriptors, form.descriptor + "0SM", "hagués / haguera ")
    form.singular2 = _get_variants(descriptors, form.descriptor + "0SM", "haguessis / hagueres ")
    form.singular3 = _get_variants(descriptors, form.descriptor + "0SM", "hagués / haguera ")

    form.plural1 = _get_variants(descriptors, form.descriptor + "0SM", "haguéssim / haguérem ")
    form.plural2 = _get_variants(descriptors, form.descriptor + "0SM", "haguéssiu / haguéreu ")
    form.plural3 = _get_variants(descriptors, form.descriptor + "0SM", "haguessin / hagueren ")


def _build_infinitive_descriptors(lines, infinitives):

    #key = infinitive
    #           value dict {}
    #                   key = descriptor
    #                   value = flexionada
    inf_desc = {}
    for line in lines:

        wordList = re.sub("[^(\w|·)]", " ",  line).split()
        flexionada = wordList[0]
        infinitive = wordList[1]
        descriptor = wordList[2]

        if infinitive in inf_desc:
            descriptors = inf_desc[infinitive]
        else:
            descriptors = {}

        if descriptor not in descriptors:
            descriptors[descriptor] = flexionada
        else:
            term = descriptors[descriptor]
            term += " / " + flexionada
            descriptors[descriptor] = term

        inf_desc[infinitive] = descriptors;

    return inf_desc


# Forms' documentation:
# https://freeling-user-manual.readthedocs.io/en/latest/tagsets/tagset-ca/#part-of-speech-verb
def _get_forms(inf_desc, req_infinitive):

    forms = []
    verb_types = ['M', 'A', 'S']

    for verb_type in verb_types:
    
        descriptors = inf_desc[req_infinitive]
        form = 'V{0}N00000'.format(verb_type)

        if form not in descriptors:
            continue

        forms.append(Forms('Indicatiu', 'Present', 'V' + verb_type + 'IP'))
        forms.append(Forms('Indicatiu', 'Perfet', 'V' + verb_type + 'P0'))
        _set_perfet_indicatiu(forms[-1], descriptors)
        forms.append(Forms('Indicatiu', 'Imperfet', 'V' + verb_type + 'II'))
        forms.append(Forms('Indicatiu', 'Plusquamperfet', 'V' + verb_type + 'P0'))
        _set_plusquamperfet_indicatiu(forms[-1], descriptors)
        forms.append(Forms('Indicatiu', 'Passat simple', 'V' + verb_type + 'IS'))
        forms.append(Forms('Indicatiu', 'Passat perifràstic', 'V' + verb_type + 'N0'))
        _set_passatperifrastic_indicatiu(forms[-1], descriptors)
        forms.append(Forms('Indicatiu', 'Passat anterior', 'V' + verb_type + 'P0'))
        _set_passatanterior_indicatiu(forms[-1], descriptors)
        forms.append(Forms('Indicatiu', 'Passat anterior perifràstic', 'V' + verb_type + 'P0'))
        _set_passatanteriorperifrastic_indicatiu(forms[-1], descriptors)
        forms.append(Forms('Indicatiu', 'Futur', 'V' + verb_type + 'IF'))
        forms.append(Forms('Indicatiu', 'Futur perfet', 'V' + verb_type + 'P0'))
        _set_futurperfet_indicatiu(forms[-1], descriptors)
        forms.append(Forms('Indicatiu', 'Condicional', 'V' + verb_type + 'IC'))
        forms.append(Forms('Indicatiu', 'Condicional perfet', 'V' + verb_type + 'P0'))
        _set_condicionalperfet_indicatiu(forms[-1], descriptors)

        forms.append(Forms('Subjuntiu', 'Present', 'V' + verb_type + 'SP'))
        forms.append(Forms('Subjuntiu', 'Perfet', 'V' + verb_type + 'P0'))
        _set_perfet_subjuntiu(forms[-1], descriptors)
        forms.append(Forms('Subjuntiu', 'Imperfet', 'V' + verb_type + 'SI'))
        forms.append(Forms('Subjuntiu', 'Plusquamperfet', 'V' + verb_type + 'P0'))
        _set_plusquamperfet_subjuntiu(forms[-1], descriptors)

        forms.append(Forms('Imperatiu', 'Present', 'V' + verb_type + 'M0'))

        for form in forms:
            _set_plurals_singulars(form, descriptors)

        forms.append(Forms('Formes no personals', 'Infinitiu', 'V' + verb_type + 'N0'))
        _set_plurals_singulars0(forms[-1], descriptors)
        forms.append(Forms('Formes no personals', 'Infinitiu compost', 'V' + verb_type + 'P0'))
        _set_infinitiu_compost(forms[-1], descriptors)
        forms.append(Forms('Formes no personals', 'Gerundi', 'V' + verb_type + 'G0'))
        _set_plurals_singulars0(forms[-1], descriptors)
        forms.append(Forms('Formes no personals', 'Gerundi compost', 'V' + verb_type + 'P0'))
        _set_gerundi_compost(forms[-1], descriptors)

        forms.append(Forms('Formes no personals', 'Participi', 'V' + verb_type + 'P0'))
        _set_plurals_singulars_participi(forms[len(forms) - 1], descriptors)

    return forms

def _serialize_to_file(file_dir, infinitive, forms):
    d = {}
    d[infinitive] = forms
    s = json.dumps(d, default=lambda x: x.__dict__, indent=4)

    with open(os.path.join(file_dir, infinitive + ".json") ,"w") as file:
        file.write(s)


def extract_from_dictfile(input_file, output_dir):
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
            print(form)

        verbs[infinitive] = forms
        _serialize_to_file(file_dir, infinitive, forms)

    return len(verbs)

def main():

    input_file = 'catalan-dict-tools/resultats/lt/diccionari.txt'
    output_dir = 'data/jsons/'

    start_time = datetime.datetime.now()

    print("Read a dictionary file and extracts the verbs into json files")
    print("Input file: {0}, output dir: {1}".format(input_file, output_dir))

    num_verbs = extract_from_dictfile(input_file, output_dir)

    print("Number of verbs {0}".format(num_verbs))
    s = 'Time used for generation: {0}'.format(datetime.datetime.now() - start_time)
    print(s)

if __name__ == "__main__":
    main()
