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

from flask import Flask, request, Response
import sys
import json
from jinja2 import Environment, FileSystemLoader

sys.path.append('models/')
from search import Search
from autocomplete import Autocomplete
from indexletter import IndexLetter

app = Flask(__name__)


# API calls
def json_answer(data):
    resp = Response(data, mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

def json_answer_status(data, status):
    resp = json_answer(data)
    resp.status = str(status)
    return resp

@app.route('/search/<word>', methods=['GET'])
def search_api(word):
    search = Search(word)
    j, status = search.get_json_search()
    return json_answer_status(j, status)

@app.route('/index/<lletra>', methods=['GET'])
def index_letter_api(lletra):
    indexLetter = IndexLetter(lletra)
    j, status = indexLetter.get_json()
    return json_answer_status(j, status)

@app.route('/autocomplete/<word>', methods=['GET'])
def autocomplete_api(word):
    autocomplete = Autocomplete(word)
    j, status = autocomplete.get_json()
    return json_answer_status(j, status)


if __name__ == '__main__':
    app.debug = True
    app.run()
