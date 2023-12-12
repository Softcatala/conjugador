#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 Joan Montané <jmontane@softcatala.org>
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

class Notes:

    def __init__(self):
        self.notes = set()

    def load_notes(self):
        notes_file = 'notes.json'

        with open(notes_file) as json_file:
             notes = json.load(json_file)
             
        print(f"Read {len(notes)} notes")
             
        self.notes = notes

    def get_note(self, lemma):
        if lemma not in self.notes:
            note = notes[lemma]
        else
            note = ''
 
        return note
        
        
