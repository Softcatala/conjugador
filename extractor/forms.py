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

class Form:
    def __init__(self, word, variant):
        self.word = word
        self.variant = variant

    def __str__(self):
        return "{0} - {1} ".format(self.word, self.variant)

class Forms:

    def __init__(self, group, form, descriptor):
        self.group = group
        self.form = form
        self.descriptor = descriptor
        self.singular1 = []
        self.singular2 = []
        self.singular3 = []
        self.plural1 = []
        self.plural2 = []
        self.plural3 = []

    def __str__(self):
        s = "---"
# [x.upper() for x in ["a","b","c"]]
        s += "* {0} ({1})\n".format(self.form,  self.group)
        s += '{0}\n'.format(''.join(str(p) for p in self.singular1))
        s += '{0}\n'.format(''.join(str(p) for p in self.singular2))
        s += '{0}\n'.format(''.join(str(p) for p in self.singular3))
        s += '{0}\n'.format(''.join(str(p) for p in self.plural1))
        s += '{0}\n'.format(''.join(str(p) for p in self.plural2))
        s += '{0}\n'.format(''.join(str(p) for p in self.plural3))
        return s
