#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2015 Jordi Mas i Hernandez <jmas@softcatala.org>
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
from io import StringIO
import re

class TextExtract:

    def __init__(self, text):
        self.text = text

    def _remove_gallery_sections(self, line):
        SECTION_START = '&lt;gallery&gt;'
        SECTION_END = '&lt;/gallery&gt;'

        start = line.find(SECTION_START)
        if start < 0:
            return line

        end = line.find(SECTION_END, start)
        if end < 0:
            return line

        final = line[:start] + line[end + len(SECTION_END) :len(line)]
        return final
        return self._remove_intenal_links(final)
        

    '''Wiki internal link with format [[LINK|TEXT]]'''
    def _remove_intenal_links(self, line):
        SECTION_START = '[['
        SECTION_END = ']]'

        start = line.find(SECTION_START)
        if start < 0:
            return line

        end = line.find(SECTION_END, start)
        if end < 0:
            return line

        '''[[CONTENT]]'''
        original = line[start:end + len(SECTION_END)]

        LINK_SEPARATOR = '|'
        start_lsp = line.find(LINK_SEPARATOR, start)
        if start_lsp < 0:
            text = line[start + len(SECTION_START) : end]
        else:
            text = line[start_lsp + len(LINK_SEPARATOR) : end]            

        final = line[:start] + text + line[end + len(SECTION_END) :len(line)]
        logging.debug("Removed link '{0}' -> '{1}'".format(line, final))

        return self._remove_intenal_links(final)

    def _remove_mediawiki_markup(self, line):
        MEDIAWIKI_BOLD = "'''"
        MEDIAWIKI_ITALIC = "''"

        final = line.replace(MEDIAWIKI_BOLD, '')
        final = final.replace(MEDIAWIKI_ITALIC, '')
        return final

    def _remove_templates(self, line):
        SECTION_START = '{{'
        SECTION_END = '}}'
        start_pos = - 1
        end_pos = -1
        pos = 0
        opened = 0
        while True:
            start = line.find(SECTION_START, pos)
            end = line.find(SECTION_END, pos)
            if start < 0 and end < 0:
                break

            if start_pos >= 0 and opened == 0:
                break

            if end < 0 or (start >= 0 and start < end):
                pos = start + len(SECTION_START)
                opened += 1
                if start_pos < 0:
                    start_pos = start
            elif start < 0 or (end >= 0 and start > end):
                pos = end + len(SECTION_END)
                end_pos = pos
                opened -= 1
            else:
                return line

        if start_pos < 0 or end_pos < 0:
            return line

        final = line[:start_pos] + line[end_pos:len(line)]
        return self._remove_templates(final)

    # Remove html tags and remove '<ref>' by ' <i>'
    def _remove_xml_tags(self, line):
        line = re.sub(r'(<ref>)(.*)(</ref>)', r' {I}\2{/I}', line)
        line = re.sub(r'<[^>]*>', '', line)
        line = re.sub(r'{I}', r'<i>', line)
        line = re.sub(r'{/I}', r'</i>', line)
        return line

    def _convert_to_html(self, line, open_ol, open_dl):
        line, open_ol = self._html_to_ol(line, open_ol)
        line, open_dl = self._html_to_dl(line, open_dl)
        return line, open_ol, open_dl

    def _html_to_ol(self, line, open_ol):
        html = line.strip()
        if len(html) > 1 and html[0] == "#" and html[1] != ":":

            text = html[1:].strip()
            if len(text) == 0:
                return '', False

            new_line = ''

            if open_ol is False:
                new_line = '<ol>'
                open_ol = True

            new_line += f"<li>{text}</li>"
            return new_line, open_ol
        elif open_ol is True and html[0:2] != "#:":
            return '</ol>' +  line, False

        return line, open_ol


    def _html_to_dl(self, line, open_dl):
        html = line.strip()
        if len(html) > 1 and html[0:2] == "#:":

            text = html[2:].strip()
            if len(text) == 0:
                return '', False

            new_line = ''

            if open_dl is False:
                new_line = '<dl>'
                open_dl = True

            new_line += f"<dd>{text}</dd>"
            return new_line, open_dl
        elif open_dl is True:
            return '</dl>' +  line, False

        return line, False

    # Extracts alternative_word from expression '{{forma-a|ca|([a-z]alternative_word)}}'¡
    def _get_alternative_form(self, s):
        FORM = r'.*{{forma-a\|ca\|([a-zàéèíóòú·ç]*)}}.*'

        alternative = ""
        _match = re.search(FORM, s)
        if _match is not None:
            count = len(_match.groups())
            if count > 0:
                alternative = _match.group(1)

        return alternative

    def _is_there_text(self, s):
        return re.search('[a-zA-Z]', s)

    def GetDescription(self, infinitives = []):
        verb = ''
        VERB_START = '===[ ]*Verb[ ]*==='
       
        found = True
        match = re.search(VERB_START, self.text)
        if match is None:
            found = False

        if found is True:
            start = match.end()
            end = self.text.find('==', start)
            if end < 0:
                found = False

        if found is False:
            return verb

        s = self.text[start:end]
        buf = StringIO(s)

        open_ol = False
        open_dl = False
        alternative = ""
        while True:
            s = buf.readline()
            if len(s) == 0:
                break

            # If we find a {{-sin-}}, {{-trad-}}, etc, stop processing
            if '{{-' in s.lower():
                break

            if len(alternative) == 0:
                alternative = self._get_alternative_form(s)

            s = self._remove_templates(s)
            s = self._remove_intenal_links(s)
            s = self._remove_mediawiki_markup(s)
            s = self._remove_xml_tags(s)
            s, open_ol, open_dl = self._convert_to_html(s, open_ol, open_dl)

            if not self._is_there_text(s):
                logging.debug("Discard:" + s)
                continue

            verb += s
            

        if alternative:
            if alternative in infinitives:
                if not self._is_there_text(s):
                    s = ""
                verb += f"<p style='font-weight: 300'>Forma alternativa a <a href='/conjugador-de-verbs/verb/{alternative}'>{alternative}</a></p>"
            else:
                logging.debug(f"alternative '{alternative}' not in infinitives")

        return verb
