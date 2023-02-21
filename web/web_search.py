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

sys.path.append('models/')
from search import Search
from autocomplete import Autocomplete
from indexletter import IndexLetter
from usage import Usage
import logging
import logging.handlers
import os
import time
import datetime
import json
from functools import lru_cache
import psutil
import datetime

app = Flask(__name__)
start_time = datetime.datetime.now()


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

@lru_cache(maxsize=500) # Rationale: there are ~10K infitives, cache top 5%
def _get_search(word):
    search = Search(word)
    j, status = search.get_json_search()
    num_results = search.get_num_results()
    return j, status, num_results

@app.route('/search/<word>', methods=['GET'])
def search_api(word):
    start_time = time.time()

    j, status, num_results = _get_search(word)

    elapsed_time = time.time() - start_time
    logging.debug(f"/search for '{word}': {num_results} results, time: {elapsed_time:.2f}s")
    Usage().log("search", elapsed_time)
    return json_answer_status(j, status)

@lru_cache(maxsize=23) # Rationale: there 23 index files only
def _get_letter_index(letter):
    indexLetter = IndexLetter(letter)
    j, status = indexLetter.get_json()
    num_results = indexLetter.get_num_results()
    return j, status, num_results

@app.route('/index/<letter>', methods=['GET'])
def index_letter_api(letter):
    start_time = time.time()

    j, status, num_results = _get_letter_index(letter)
    elapsed_time = time.time() - start_time
    logging.debug(f"/index for '{letter}': {num_results} results, time: {elapsed_time:.2f}s")
    Usage().log("index", elapsed_time)
    return json_answer_status(j, status)

@app.route('/autocomplete/<word>', methods=['GET'])
def autocomplete_api(word):
    start_time = time.time()

    autocomplete = Autocomplete(word)
    j, status = autocomplete.get_json()
    num_results = autocomplete.get_num_results()

    elapsed_time = time.time() - start_time
    logging.debug(f"/autocomplete for '{word}': {num_results} results, time: {elapsed_time:.2f}s")
    Usage().log("autocomplete", elapsed_time)
    return json_answer_status(j, status)

def _get_cache_info(cache_info):
    cache = {}

    hits = cache_info.hits
    misses = cache_info.misses

    total = hits + misses
    phits = (hits * 100 / total) if total else 0

    cache['misses'] = f"{misses}"
    cache['hits'] = f"{hits} ({phits:.2f}%)"
    return cache

@app.route('/stats/', methods=['GET'])
def stats():
    requested = request.args.get('date')
    date_requested = datetime.datetime.strptime(requested, '%Y-%m-%d')
    usage = Usage()
    result = usage.get_stats(date_requested)
    rss = psutil.Process(os.getpid()).memory_info().rss // 1024 ** 2

    caches =  {}
    cache_info = _get_letter_index.cache_info()
    caches['search'] = _get_cache_info(_get_search.cache_info())
    cache_info = _get_letter_index.cache_info()
    caches['letter_index'] = _get_cache_info(_get_letter_index.cache_info())
    result['cache'] = caches

    result['process_id'] = os.getpid()
    result['rss'] = f"{rss} MB"
    result['up_time'] = str(datetime.datetime.now() - start_time)

    json_data = json.dumps(result, indent=4, separators=(',', ': '))
    return json_answer(json_data)

if __name__ == '__main__':
    init_logging()
    app.debug = True
    app.run()

if __name__ != '__main__':
    init_logging()
