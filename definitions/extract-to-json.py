#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
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

import datetime
import logging
import os
from definitions import Definitions

def init_logging():
    logfile = 'extract-to-json.log'

    if os.path.isfile(logfile):
        os.remove(logfile)

    logging.basicConfig(filename=logfile, level=logging.DEBUG)

def main():

    print("Reads a Wikidictionary XML dump and extracts verbs defintions")
    init_logging()
    start_time = datetime.datetime.now()

    definitions = Definitions()
    definitions.generate('definitions/cawiktionary-latest-pages-meta-current.xml')

    msg = 'Time {0}'.format(datetime.datetime.now() - start_time)
    logging.info(msg)

if __name__ == "__main__":
    main()
