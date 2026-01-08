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

from elasticsearch import Elasticsearch


class BaseSearch:
    """
    Base class that provides functionality to store a word for later search.
    """

    DEFAULT_ES_HOST = "http://localhost:9200"

    def __init__(self, word: str, es_url: str = DEFAULT_ES_HOST) -> None:
        """
        Initializes the SearchBase class with a word.

        Args:
            word (str): The word to search.
            es_url (str): The url of the Elasticsearch instance to connect to.
        """
        self._word = word
        self.es_client = Elasticsearch(es_url)

    @property
    def word(self) -> str:
        """
        Gets the current word.
        """
        return self._word
