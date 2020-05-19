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
import logging
import logging.handlers
import os
import time

app = Flask(__name__)

def init_logging():
    logfile = 'web-service.log'

    LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
    logger = logging.getLogger()
    hdlr = logging.handlers.RotatingFileHandler(logfile, maxBytes=1024*1024, backupCount=1)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(LOGLEVEL)

    console = logging.StreamHandler()
    console.setLevel(LOGLEVEL)
    logger.addHandler(console)


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
    start_time = time.time()

    search = Search(word)
    j, status = search.get_json_search()
    num_results = search.get_num_results()

    elapsed_time = time.time() - start_time
    logging.debug(f"/search for '{word}': {num_results} results, time: {elapsed_time:.2f}s")
    return json_answer_status(j, status)

@app.route('/index/<lletra>', methods=['GET'])
def index_letter_api(lletra):
    logging.debug(f"/index for '{lletra}'")
    indexLetter = IndexLetter(lletra)
    j, status = indexLetter.get_json()
    return json_answer_status(j, status)

@app.route('/autocomplete/<word>', methods=['GET'])
def autocomplete_api(word):
    start_time = time.time()

    autocomplete = Autocomplete(word)
    j, status = autocomplete.get_json()
    num_results = autocomplete.get_num_results()

    elapsed_time = time.time() - start_time
    logging.debug(f"/autocomplete for '{word}': {num_results} results, time: {elapsed_time:.2f}s")
    return json_answer_status(j, status)


if __name__ == '__main__':
    init_logging()
    app.debug = True
    app.run()

if __name__ != '__main__':
    init_logging()
