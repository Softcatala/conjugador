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
from optparse import OptionParser
from forms import Tense
from forms import Form


def _read_file(input_file):
    with open(input_file) as f:
        return f.readlines()

def _get_lemmas(lines):

    INFINITIVE_DESCRIPTORS = set(['VMN00000', 'VAN00000', 'VSN00000'])

    lemmas = []
    for line in lines:
        form, lemma, postag = _get_form_lemma_postag_from_line(line)

        if postag not in INFINITIVE_DESCRIPTORS:
            continue

        lemmas.append(lemma)

    return lemmas

def _add_separator(result):
    if len(result) > 0:
        result += " - "

    return result

def _get_forms_with_variant(lemma_subdict, postag, prefix=''):

    result = []

    variants = ["0", "1", "2", "3", "4", "5", "6", "7", "C", "X", "Y", "Z", "V", "B"]

    for variant in variants:
        word = lemma_subdict.get(postag + variant);
        if word is not None:
            result.append(Form(word, variant, prefix))

    return result

def _get_verb_mode(postag):
    return postag[2]

def _set_plurals_singulars(tense, lemma_subdict):
    if _get_verb_mode(tense.postag) not in ['I', 'S', 'M']:
        return
    tense.singular1 = _get_forms_with_variant(lemma_subdict, tense.postag + "1S0")
    tense.singular2 = _get_forms_with_variant(lemma_subdict, tense.postag + "2S0")
    tense.singular3 = _get_forms_with_variant(lemma_subdict, tense.postag + "3S0")

    tense.plural1 = _get_forms_with_variant(lemma_subdict, tense.postag + "1P0")
    tense.plural2 = _get_forms_with_variant(lemma_subdict, tense.postag + "2P0")
    tense.plural3 = _get_forms_with_variant(lemma_subdict, tense.postag + "3P0")

def _set_plurals_singulars_participi(tense, lemma_subdict):
    if _get_verb_mode(tense.postag) != 'P':
        return
    tense.singular1 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM")
    tense.singular2 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SF")
    tense.singular3 = _get_forms_with_variant(lemma_subdict, tense.postag + "0PM")
    tense.plural1 = _get_forms_with_variant(lemma_subdict, tense.postag + "0PF")


def _set_plurals_singulars0(tense, lemma_subdict):
    tense.singular1 = _get_forms_with_variant(lemma_subdict, tense.postag + "000")

def _set_infinitiu_compost(tense, lemma_subdict):
    if _get_verb_mode(tense.postag) != 'P':
        return
    tense.singular1 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "haver ")

def _set_gerundi_compost(tense, lemma_subdict):
    if _get_verb_mode(tense.postag) != 'P':
        return
    tense.singular1 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "havent ")

def _set_perfet_indicatiu(tense, lemma_subdict):
    if _get_verb_mode(tense.postag) != 'P':
        return
    tense.singular1 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "he ")
    tense.singular2 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "has ")
    tense.singular3 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "ha ")

    tense.plural1 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "hem ")
    tense.plural2 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "heu ")
    tense.plural3 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "han ")

def _set_plusquamperfet_indicatiu(tense, lemma_subdict):
    if _get_verb_mode(tense.postag) != 'P':
        return
    tense.singular1 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "havia ")
    tense.singular2 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "havies ")
    tense.singular3 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "havia ")

    tense.plural1 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "havíem ")
    tense.plural2 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "havíeu ")
    tense.plural3 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "havien ")

def _set_passatperifrastic_indicatiu(tense, lemma_subdict):
    if _get_verb_mode(tense.postag) != 'N':
        return
    tense.singular1 = _get_forms_with_variant(lemma_subdict, tense.postag + "000", "vaig ")
    tense.singular2 = _get_forms_with_variant(lemma_subdict, tense.postag + "000", "vas (vares) ")
    tense.singular3 = _get_forms_with_variant(lemma_subdict, tense.postag + "000", "va ")

    tense.plural1 = _get_forms_with_variant(lemma_subdict, tense.postag + "000", "vam (vàrem) ")
    tense.plural2 = _get_forms_with_variant(lemma_subdict, tense.postag + "000", "vau (vàreu) ")
    tense.plural3 = _get_forms_with_variant(lemma_subdict, tense.postag + "000", "van (varen) ")

def _set_passatanterior_indicatiu(tense, lemma_subdict):
    if _get_verb_mode(tense.postag) != 'P':
        return
    tense.singular1 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "haguí ")
    tense.singular2 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "hagueres ")
    tense.singular3 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "hagué ")

    tense.plural1 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "haguérem ")
    tense.plural2 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "haguéreu ")
    tense.plural3 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "hagueren ")

def _set_passatanteriorperifrastic_indicatiu(tense, lemma_subdict):
    if _get_verb_mode(tense.postag) != 'P':
        return
    tense.singular1 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "vaig haver ")
    tense.singular2 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "vas haver ")
    tense.singular3 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "va haver ")

    tense.plural1 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "vam haver ")
    tense.plural2 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "vau haver ")
    tense.plural3 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "van haver ")

def _set_futurperfet_indicatiu(tense, lemma_subdict):
    if _get_verb_mode(tense.postag) != 'P':
        return
    tense.singular1 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "hauré ")
    tense.singular2 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "hauràs ")
    tense.singular3 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "haurà ")

    tense.plural1 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "haurem ")
    tense.plural2 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "haureu ")
    tense.plural3 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "hauran ")

def _set_condicionalperfet_indicatiu(tense, lemma_subdict):
    if _get_verb_mode(tense.postag) != 'P':
        return
    tense.singular1 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "hauria (haguera) ")
    tense.singular2 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "hauries (hagueres) ")
    tense.singular3 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "hauria (haguera) ")

    tense.plural1 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "hauríem (haguérem) ")
    tense.plural2 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "hauríeu (haguéreu) ")
    tense.plural3 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "haurien (hagueren) ")

def _set_perfet_subjuntiu(tense, lemma_subdict):
    if _get_verb_mode(tense.postag) != 'P':
        return
    tense.singular1 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "hagi (haja) ")
    tense.singular2 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "hagis (hages) ")
    tense.singular3 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "hagi (haja) ")

    tense.plural1 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "hàgim (hàgem) ")
    tense.plural2 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "hàgiu (hàgeu) ")
    tense.plural3 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "hagin (hagen) ")

def _set_plusquamperfet_subjuntiu(tense, lemma_subdict):
    if _get_verb_mode(tense.postag) != 'P':
        return
    tense.singular1 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "hagués (haguera) ")
    tense.singular2 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "haguessis (hagueres) ")
    tense.singular3 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "hagués (haguera) ")

    tense.plural1 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "haguéssim (haguérem) ")
    tense.plural2 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "haguéssiu (haguéreu) ")
    tense.plural3 = _get_forms_with_variant(lemma_subdict, tense.postag + "0SM", "haguessin (hagueren) ")


def _build_dictionary(lines):

    #key = lemma (infinitive)
    #           value dict {}
    #                   key = postag
    #                   value = form
    main_dict = {}
    for line in lines:
        form, lemma, postag = _get_form_lemma_postag_from_line(line)

        if lemma in main_dict:
            lemma_subdict = main_dict[lemma]
        else:
            lemma_subdict = {}

        if postag not in lemma_subdict:
            lemma_subdict[postag] = form
        else:
            new_form = lemma_subdict[postag]
            new_form += " / " + form
            lemma_subdict[postag] = new_form

        main_dict[lemma] = lemma_subdict;

    return main_dict


# Part of speech tags documentation:
# https://freeling-user-manual.readthedocs.io/en/latest/tagsets/tagset-ca/#part-of-speech-verb
def _get_tenses(input_dict, lemma):

    tenses = []
    verb_types = ['M', 'A', 'S']

    for verb_type in verb_types:
    
        lemma_subdict = input_dict[lemma]
        infinitive_postag = 'V{0}N00000'.format(verb_type)

        if infinitive_postag not in lemma_subdict:
            continue

        tenses.append(Tense('Indicatiu', 'Present', 'V' + verb_type + 'IP'))
        tenses.append(Tense('Indicatiu', 'Perfet', 'V' + verb_type + 'P0'))
        _set_perfet_indicatiu(tenses[-1], lemma_subdict)
        tenses.append(Tense('Indicatiu', 'Imperfet', 'V' + verb_type + 'II'))
        tenses.append(Tense('Indicatiu', 'Plusquamperfet', 'V' + verb_type + 'P0'))
        _set_plusquamperfet_indicatiu(tenses[-1], lemma_subdict)
        tenses.append(Tense('Indicatiu', 'Passat simple', 'V' + verb_type + 'IS'))
        tenses.append(Tense('Indicatiu', 'Passat perifràstic', 'V' + verb_type + 'N0'))
        _set_passatperifrastic_indicatiu(tenses[-1], lemma_subdict)
        tenses.append(Tense('Indicatiu', 'Passat anterior', 'V' + verb_type + 'P0'))
        _set_passatanterior_indicatiu(tenses[-1], lemma_subdict)
        tenses.append(Tense('Indicatiu', 'Passat anterior perifràstic', 'V' + verb_type + 'P0'))
        _set_passatanteriorperifrastic_indicatiu(tenses[-1], lemma_subdict)
        tenses.append(Tense('Indicatiu', 'Futur', 'V' + verb_type + 'IF'))
        tenses.append(Tense('Indicatiu', 'Futur perfet', 'V' + verb_type + 'P0'))
        _set_futurperfet_indicatiu(tenses[-1], lemma_subdict)
        tenses.append(Tense('Indicatiu', 'Condicional', 'V' + verb_type + 'IC'))
        tenses.append(Tense('Indicatiu', 'Condicional perfet', 'V' + verb_type + 'P0'))
        _set_condicionalperfet_indicatiu(tenses[-1], lemma_subdict)

        tenses.append(Tense('Subjuntiu', 'Present', 'V' + verb_type + 'SP'))
        tenses.append(Tense('Subjuntiu', 'Perfet', 'V' + verb_type + 'P0'))
        _set_perfet_subjuntiu(tenses[-1], lemma_subdict)
        tenses.append(Tense('Subjuntiu', 'Imperfet', 'V' + verb_type + 'SI'))
        tenses.append(Tense('Subjuntiu', 'Plusquamperfet', 'V' + verb_type + 'P0'))
        _set_plusquamperfet_subjuntiu(tenses[-1], lemma_subdict)

        tenses.append(Tense('Imperatiu', 'Present', 'V' + verb_type + 'M0'))

        for tense in tenses:
            _set_plurals_singulars(tense, lemma_subdict)

        tenses.append(Tense('Formes no personals', 'Infinitiu', 'V' + verb_type + 'N0'))
        _set_plurals_singulars0(tenses[-1], lemma_subdict)
        tenses.append(Tense('Formes no personals', 'Infinitiu compost', 'V' + verb_type + 'P0'))
        _set_infinitiu_compost(tenses[-1], lemma_subdict)
        tenses.append(Tense('Formes no personals', 'Gerundi', 'V' + verb_type + 'G0'))
        _set_plurals_singulars0(tenses[-1], lemma_subdict)
        tenses.append(Tense('Formes no personals', 'Gerundi compost', 'V' + verb_type + 'P0'))
        _set_gerundi_compost(tenses[-1], lemma_subdict)

        tenses.append(Tense('Formes no personals', 'Participi', 'V' + verb_type + 'P0'))
        _set_plurals_singulars_participi(tenses[len(tenses) - 1], lemma_subdict)

    return tenses

def _serialize_to_file(file_dir, lemma, tenses):
    d = {}
    d[lemma] = tenses
    s = json.dumps(d, default=lambda x: x.__dict__, indent=4)

    with open(os.path.join(file_dir, lemma + ".json") ,"w") as file:
        file.write(s)

def _get_form_lemma_postag_from_line(line):
    wordList = re.sub("[^(\w|·)]", " ",  line).split()
    form = wordList[0]
    lemma = wordList[1]
    postag = wordList[2]
    return form, lemma, postag

def _load_definitions(definitions_file):
    with open(definitions_file) as json_file:
        data = json.load(json_file)
        return data

'''
    La forma en infinitiu "anar" no és una forma auxiliar i no apareix com a infinitiu al diccionari.
    Com a resultat totes les formes vaja, vam, van queden penjades sense mostrar-se.
'''
def _pre_process_anar_auxiliar(lines):
    lemmas = []
    for i in range(0, len(lines)):
        line = lines[i]
        form, lemma, postag = _get_form_lemma_postag_from_line(line)

        if lemma =='anar' and postag[0:2] == 'VA':
            line = f'{form} anar_aux {postag}'
            lines[i] = line

    lines.append("anar anar_aux VAN00000")
    return lines

def rename_anar_aux_infinitive(lemma, tenses):
    if lemma == 'anar_aux':

        lemma = 'anar - auxiliar'
        for i in range(0, len(tenses)):
            tense = tenses[i]
            if any(ext in tense.tense for ext in ('Passat perifràstic', 'Infinitiu')):
                tenses[i] = Tense(tense.mode, tense.tense, tense.postag)

    return lemma, tenses

def _set_definition(lemma, tenses, definitions):
    defintion = {}
    if lemma in definitions:
        defintion["definition"] = definitions[lemma]
        defintion["definition_credits"] = "La descripció del verb prové del Viccionari amb " \
        "<a https://creativecommons.org/licenses/by-sa/3.0/deed.ca>Llicència de Creative Commons Reconeixement/Compartir-Igual.</a>. " \
        f"Podeu millorar aquesta descripció fent clic a <a href='https://ca.wiktionary.org/wiki/{lemma}'>{lemma}</a>."
    else:
        defintion["definition_url"] = f"https://dlc.iec.cat/results.asp?txtEntrada={lemma}"
        defintion["definition_credits"] = "Aquest verb no existeix al Viccionari, que és la font que usem per a les definicions. " \
        f"Podeu crear-la fent clic a <a href='https://ca.wiktionary.org/wiki/{lemma}'>{lemma}</a>."

    tenses.insert(0, defintion)


def extract_from_dictfile(input_file, definitions_file, output_dir):
    lines = _read_file(input_file)
    lines = _pre_process_anar_auxiliar(lines)

    lemmas = _get_lemmas(lines)

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        os.makedirs(output_dir)

    output_dict = set()
    input_dict = _build_dictionary(lines)

    definitions = _load_definitions(definitions_file)

    for lemma in lemmas:

        #if infinitive != 'cantar':
        #    continue
        file_dir = os.path.join(output_dir, lemma[:2])
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        tenses = _get_tenses(input_dict, lemma)

        output_dict.add(lemma)
        lemma, tenses = rename_anar_aux_infinitive(lemma, tenses)

        _set_definition(lemma, tenses, definitions)
        _serialize_to_file(file_dir, lemma, tenses)

    return len(output_dict)


def extract_infinitives(input_file, output_file):

    file_dir = os.path.dirname(output_file)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    lines = _read_file(input_file)
    lines = _pre_process_anar_auxiliar(lines)
    lemmas = _get_lemmas(lines)

    with open(output_file, "w") as f_infinitives:
        f_infinitives.writelines(["%s\n" % item  for item in lemmas])

    return len(lemmas)

def read_parameters():
    parser = OptionParser()

    parser.add_option(
        '-i',
        '--infinitives-only',
        action='store_true',
        dest='infinitives_only',
        default=False,
        help='Extract infinitives only'
    )
    (options, args) = parser.parse_args()
    return options.infinitives_only

def main():

    infinitives_only = read_parameters()

    input_file = 'catalan-dict-tools/resultats/lt/diccionari.txt'
    output_dir = 'data/jsons/'
    infinitives_file = 'data/infinitives.txt'
    definitions_file = 'data/definitions.json'

    start_time = datetime.datetime.now()

    print("Read a dictionary file and extracts the verbs")

    if infinitives_only:
        print("Input file: {0}, output dir: {1}".format(input_file, infinitives_file))
        num_verbs = extract_infinitives(input_file, infinitives_file)
    else:
        print("Input file: {0}, output dir: {1}".format(input_file, output_dir))
        num_verbs = extract_from_dictfile(input_file, definitions_file, output_dir)

    print("Number of verbs {0}".format(num_verbs))
    s = 'Time used for generation: {0}'.format(datetime.datetime.now() - start_time)
    print(s)

if __name__ == "__main__":
    main()
