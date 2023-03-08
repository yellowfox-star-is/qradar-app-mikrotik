import requests
from qpylib.ariel import ArielSearch, ArielError
import json
import logging
import sys

ariel = ArielSearch()

search_state = ['COMPLETED', 'WAIT']

def search_start(query):
    try:
        response = ariel.search(query)
    except ArielError as error:
        return {"Error": str(error)}

    return response


def search_status(search_id):
    try:
        response = ariel.status(search_id)
    except ArielError as error:
        return {"Error": str(error)}

    return response


def search_results(search_id):
    try:
        # maybe add start, end to results, so we don't overload the app
        response = ariel.results(search_id)

    except ArielError as error:
        return {"Error": str(error)}
    except ValueError as error:
        return {"Range Error": str(error)}

    return response


def test_basic():
    status, search_id = search_start("SELECT * FROM events LAST 10 MINUTES")
    logging.debug((status, search_id))
    status, record_count = search_status(search_id)
    logging.debug((status, record_count))
    results = search_results(search_id)
    test0 = isinstance(results, dict)
    debug_words = lambda x: 'received expected results' if x else 'received weird results'
    logging.debug('test0: ' + debug_words(test0))
    if not test0:
        return 1
    test1 = 'events' in results.keys()
    logging.debug('test1: ' + debug_words(test1))
    if not test1:
        return 2
    test2 = len(results['events']) >= 0
    if test2:
        logging.debug("test2: Received {} results".format(len(results['events'])))
    else:
        logging.debug("test2: Didn't get any results from ariel, but rest looks OK.")
    return 0


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    test_basic()
