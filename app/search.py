import time

import requests, json, logging, sys
from custom_ariel import ArielSearch, ArielError

ariel = ArielSearch()


class States:
    Completed = 'COMPLETED'
    Wait = 'WAIT'
    Sorting = 'SORTING'
    Execute = 'EXECUTE'
    Unknown = 'unknown'

    waiting = [Wait, Sorting, Execute]


"""Timeout in seconds when waiting for search results update."""
Timeout: int = 1

__test_query = "SELECT * FROM events LAST 10 MINUTES"

log_status = lambda s: logging.debug(f"acquired status: {s}")


def search_start(query):
    try:
        response = ariel.search(query)
    except ArielError as error:
        logging.error(str(error))
        return "Error", {"Error": str(error)}

    log_status(response[0])
    return response


def search_status(search_id):
    try:
        response = ariel.status(search_id)
    except ArielError as error:
        logging.error(str(error))
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


def decide_which_timeout(timeout_func):
    if timeout_func != 0:
        return timeout_func
    return Timeout


def search(query, timeout_func=0):
    try:
        timeout_local = decide_which_timeout(timeout_func)

        status, search_id = search_start(query)
        record_count = 0

        # Loop that waits for when the search is completed.
        while True:
            status, record_count = search_status(search_id)

            if status in States.waiting:
                time.sleep(timeout_local)
                continue
            if status == States.Completed:
                break
            raise NotImplementedError(f"encountered not known search status: {status}")

        return search_results(search_id)['events']
        # NOTE XXX should search be deleted after acquiring results?

    except ArielError:
        return None


def test_basic():
    status, search_id = search_start(__test_query)
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


def test_full_search():
    results = search(__test_query)
    return len(results) > 0


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    test_basic()
    test_full_search()
