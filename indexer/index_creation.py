#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
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

import datetime

from indexer.indexcreator import IndexCreator


def main() -> None:  # noqa: D103
    print("Create Elasticsearch indices from a directory with JSONs")

    start_time = datetime.datetime.now()

    index_creator = IndexCreator("data/jsons/")
    index_creator.process_files()
    print(
        "Time used to create the index: {0} ".format(
            datetime.datetime.now() - start_time
        )
    )


if __name__ == "__main__":
    main()
