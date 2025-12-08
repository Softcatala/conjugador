# -*- coding: utf-8 -*-
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

import unittest

from definitions.textextract import TextExtract


class TestTextExtract(unittest.TestCase):


    def test_convert_to_html_simple_num_list(self):
        src = '''abaltir
#  Endormiscar, mig dormir.
#  Endormiscar-se.
'''
        open_ol = False
        open_dl = False
        lines = src.split("\n")
        htmls = []

        html = ''
        for line in lines:
            textExtract = TextExtract(line)

            html, open_ol, open_dl = textExtract._convert_to_html(line, open_ol=open_ol, open_dl=open_dl)
            htmls.append(html)

        self.assertEqual(4, len(htmls))
        self.assertEqual("abaltir", htmls[0])
        self.assertEqual("<ol><li>Endormiscar, mig dormir.</li>", htmls[1])
        self.assertEqual("<li>Endormiscar-se.</li>", htmls[2])
        self.assertEqual("</ol>", htmls[3])

    def test_convert_to_html_simple_num_list_with_description_list(self):
        src = '''arrambar
# Posar coses juntes a un costat.
#  Acostar-se molt a una cosa fins a tocar-la.
#: «Vaig arrambar-me d'esquena a la paret»
#: «Alerta, no t'arrambis pel balcó que pots caure»
#  Llançar la pilota de manera que es desplaci arran de paret.
'''
        open_ol = False
        open_dl = False
        lines = src.split("\n")
        htmls = []

        html = ''
        for line in lines:
            textExtract = TextExtract(line)

            html, open_ol, open_dl = textExtract._convert_to_html(line, open_ol=open_ol, open_dl=open_dl)
            htmls.append(html)

        self.assertEqual(7, len(htmls))
        self.assertEqual("arrambar", htmls[0])
        self.assertEqual("<ol><li>Posar coses juntes a un costat.</li>", htmls[1])
        self.assertEqual("<li>Acostar-se molt a una cosa fins a tocar-la.</li>", htmls[2])
        self.assertEqual("<dl><dd>«Vaig arrambar-me d'esquena a la paret»</dd>", htmls[3])
        self.assertEqual("<dd>«Alerta, no t'arrambis pel balcó que pots caure»</dd>", htmls[4])
        self.assertEqual("</dl><li>Llançar la pilota de manera que es desplaci arran de paret.</li>", htmls[5])
        self.assertEqual("</ol>", htmls[6])

    def test_remove_xml_tags_tags(self):
        line = '''Perjudicar la parença d'algú. <i>És un vestit que la desparença molt</i>.'''

        textExtract = TextExtract(line)
        text = textExtract._remove_xml_tags(line)

        self.assertEqual("Perjudicar la parença d'algú. És un vestit que la desparença molt.", text)

    def test_remove_xml_tags_href(self):
        line = '''Pantalons de rodamón lligats amb un cordill.<ref>Barbara Kingsolver, 2010</ref>'''

        textExtract = TextExtract(line)
        text = textExtract._remove_xml_tags(line)

        self.assertEqual("Pantalons de rodamón lligats amb un cordill. <i>Barbara Kingsolver, 2010</i>", text)

    def test_get_remove_templates_single(self):
        line = 'Això és un {{ca.v.conj.para1|dom}} text'
        textExtract = TextExtract(line)
        text = textExtract._remove_templates(line)

        self.assertEqual("Això és un  text", text)

    def test_get_remove_templates_double_neested(self):
        line = 'Això és un {{ex-us|ca|Cal diferenciar el català del segle {{romanes|XV}} del català del segle {{romanes|XVI}}.}} text'
        textExtract = TextExtract(line)
        text = textExtract._remove_templates(line)

        self.assertEqual("Això és un  text", text)

    def test_get_remove_templates_double(self):
        line = '{{marca|ca|mallorquí|menorquí}} [[ensumar|Ensumar]] {{q|aspirar}}'
        textExtract = TextExtract(line)
        alternative = textExtract._remove_templates(line)

        self.assertEqual(" [[ensumar|Ensumar]] ", alternative)

    def test_get_alternative_form_form(self):
        line = '''{{es-verb|t|present=acenso}} {{forma-a|ca|complànyer}}'''
        textExtract = TextExtract(line)
        alternative = textExtract._get_alternative_form(line)

        self.assertEqual("complànyer", alternative)

    def test_get_alternative_form_no_form(self):
        line = '''{{es-verb|t|present=acenso}} {{forma-a|es|cantar}}'''
        textExtract = TextExtract(line)
        alternative = textExtract._get_alternative_form(line)

        self.assertEqual("", alternative)
        
    def test_remove_gallery_sections(self):
    
        line = '''Inici <gallery>;
Fitxer:30 Days of Gratitude- Day 25 (4130230553).jpg|Gos amb ulleres [1]
Fitxer:Chess-familienschach.PNG|Exemple d'ulleres o forquilla [4] 
</gallery> Fi'''

        textExtract = TextExtract(line)
        text = textExtract._remove_gallery_sections(line)

        self.assertEqual("Inici  Fi", text)

if __name__ == '__main__':
    unittest.main()
    
