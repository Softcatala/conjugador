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

class Forms:

    def __init__(self, group, form, descriptor):
        self.group = group
        self.form = form
        self.descriptor = descriptor
        self.singular1 = '-'
        self.singular2 = '-'
        self.singular3 = '-'
        self.plural1 = '-'
        self.plural2 = '-'
        self.plural3 = '-'
        self.variants = ''

    def print(self):
        print("---")
        print("* {0} ({1})".format(self.form,  self.group))
        print(self.singular1)
        print(self.singular2)
        print(self.singular3)
        print(self.plural1)
        print(self.plural2)
        print(self.plural3)


