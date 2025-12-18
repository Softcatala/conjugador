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
import json
import logging
import logging.handlers
import os
import time
from functools import _CacheInfo, lru_cache
from pathlib import Path

import psutil
from flask import Flask, Response, request

from web.models.autocomplete import Autocomplete
from web.models.indexletter import IndexLetter
from web.models.search import Search
from web.usage import Usage

app = Flask(__name__)
start_time = datetime.datetime.now()
es_url = os.getenv("ES_URL", "http://conjugador-elastic:9200")
es_logger = logging.getLogger("elastic_transport.transport")
es_logger.setLevel(os.getenv("LOGLEVEL", "WARNING"))


def init_logging() -> None:
    """
    Initializes all the logging environment such as the Log Level, and Log File.
    """
    LOGDIR = os.environ.get("LOGDIR", "")
    LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
    logger = logging.getLogger()
    logfile = Path(LOGDIR) / "web-service.log"
    hdlr = logging.handlers.RotatingFileHandler(
        logfile, maxBytes=1024 * 1024, backupCount=1
    )
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(LOGLEVEL)

    console = logging.StreamHandler()
    console.setLevel(LOGLEVEL)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console.setFormatter(formatter)
    logger.addHandler(console)


# API calls
def json_answer(data: str) -> Response:
    """
    Envelopes a JSON string into a Flask response and adds CORS headers.

    Args:
        data (str): The JSON string to use as a response body.

    Returns:
        Response: A flask response with the body and headers applied.
    """
    resp = Response(data, mimetype="application/json")
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


def json_answer_status(data: str, status: int) -> Response:
    """
    Envelopes a JSON string and a status code into a Flask Response.

    Args:
        data (str): The JSON string to use as response body.
        status (int): The status code to apply to the response.

    Returns:
        Response: A Flask response with the body, headers and status code applied.
    """
    resp = json_answer(data)
    resp.status = str(status)
    return resp


@lru_cache(maxsize=500)  # Rationale: there are ~10K infitives, cache top 5%
def _get_search(word: str) -> tuple[str, int, int]:
    search = Search(word, es_url)
    j, status = search.get_json_search()
    num_results = search.get_num_results()
    return j, status, num_results


@app.route("/search/<word>", methods=["GET"])
def search_api(word: str) -> Response:
    """
    Endpoint for the search functionality. Allows the user to input a word as
    a query parameter and check for verbs matching it or their conjugations.
    """
    start_time = time.time()

    j, status, num_results = _get_search(word)

    elapsed_time = time.time() - start_time
    logging.debug(
        f"/search for '{word}': {num_results} results, time: {elapsed_time:.2f}s"
    )
    return json_answer_status(j, status)


@lru_cache(maxsize=23)  # Rationale: there 23 index files only
def _get_letter_index(letter: str) -> tuple[str, int, int]:
    indexLetter = IndexLetter(letter, es_url)
    j, status = indexLetter.get_json()
    num_results = indexLetter.get_num_results()
    return j, status, num_results


@app.route("/index/<letter>", methods=["GET"])
def index_letter_api(letter: str) -> Response:
    """
    Endpoint for the letter index functionality. Allows the user to input a letter as
    a query parameter and check all the verbs starting with that letter.
    """
    start_time = time.time()

    j, status, num_results = _get_letter_index(letter)
    elapsed_time = time.time() - start_time
    logging.debug(
        f"/index for '{letter}': {num_results} results, time: {elapsed_time:.2f}s"
    )
    return json_answer_status(j, status)


@lru_cache(maxsize=500)
def _get_autocomplete(word: str) -> tuple[str, int, int]:
    autocomplete = Autocomplete(word, es_url)
    j, status = autocomplete.get_json()
    num_results = autocomplete.get_num_results()
    return j, status, num_results


@app.route("/autocomplete/<word>", methods=["GET"])
def autocomplete_api(word: str) -> Response:
    """
    Endpoint for the autocomplete functionality. Allows the user to input a piece of
    a verb as a query parameter and checks all the verbs that match the pattern.
    """
    start_time = time.time()

    j, status, num_results = _get_autocomplete(word)
    elapsed_time = time.time() - start_time
    logging.debug(
        f"/autocomplete for '{word}': {num_results} results, time: {elapsed_time:.2f}s"
    )
    return json_answer_status(j, status)


def _get_cache_info(cache_info: _CacheInfo) -> dict:
    cache = {}

    hits = cache_info.hits
    misses = cache_info.misses

    total = hits + misses
    phits = (hits * 100 / total) if total else 0

    cache["misses"] = f"{misses}"
    cache["hits"] = f"{hits} ({phits:.2f}%)"
    return cache


@app.route("/stats/", methods=["GET"])
def stats() -> Response:
    """
    This endpoint retrieves all the stats of the API, uptime, process id,
    MBs and cache information.
    """
    try:
        requested = request.args.get("date")
        date_requested = datetime.datetime.strptime(
            requested,  # pyrefly: ignore
            "%Y-%m-%d",
        )
    except Exception:
        return Response({}, mimetype="application/json", status=400)

    usage = Usage()
    result = usage.get_stats(date_requested)
    rss = psutil.Process(os.getpid()).memory_info().rss // 1024**2

    caches = {}
    caches["search"] = _get_cache_info(_get_search.cache_info())
    caches["letter_index"] = _get_cache_info(_get_letter_index.cache_info())
    caches["autocomplete"] = _get_cache_info(_get_autocomplete.cache_info())
    result["cache"] = caches

    result["process_id"] = os.getpid()
    result["rss"] = f"{rss} MB"
    result["up_time"] = str(datetime.datetime.now() - start_time)

    json_data = json.dumps(result, indent=4, separators=(",", ": "))
    return json_answer(json_data)


if __name__ == "__main__":
    init_logging()
    app.debug = True  # pyrefly: ignore
    app.run()

if __name__ != "__main__":
    init_logging()
