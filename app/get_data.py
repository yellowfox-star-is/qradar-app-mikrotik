import copy

import search
import json
import objects
from qpylib import qpylib

event_source_type_name = "Mikrotik RouterOS"


def get_all():
    routers = get_routers()
    result = []
    for router in routers:
        result.append(objects.init_router())
        result[-1]["name"] = router["name"]
        result[-1]["networks"] = get_networks(router["id"])
        result[-1]["offenses"] = get_offenses(router["id"])
        result[-1]["devices"] = get_devices(router["id"])
    return result


def get_event_source_type_id():
    # get response
    params = {
        'filter': f'name="{event_source_type_name}"',
        'Range': 'items=0-49'
    }
    response = qpylib.REST(rest_action='GET',
                           request_url='/api/config/event_sources/log_source_management/log_source_types',
                           params=params)

    # parse response
    data = response.json()

    # there should be only one log source type of this name
    if len(data) > 1:
        raise NotImplementedError(f'Got more than one Log Source type of name: "{event_source_type_name}".')
    return data[0]["id"]


def get_routers():
    # get response
    event_source_id = get_event_source_type_id()
    params = {
        "filter": f"type_id={event_source_id}"
    }
    response = qpylib.REST(rest_action="GET",
                           request_url="/api/config/event_sources/log_source_management/log_sources",
                           params=params)

    # parse response
    data = response.json()

    # take desirable data and put it into list of dictionaries
    result = []
    for router in data:
        new = {
            "name": copy.deepcopy(router["name"]),
            "id": copy.deepcopy(router["id"])
         }
        result.append(new)

    return result


if __name__ == "__main__":
    routers = get_routers()
    print(routers)
    search_results = search.search(f"SELECT * FROM events WHERE logsourceid = {routers[0]['id']} LAST 7 DAYS")
    print(json.dumps(search_results, indent=4))
    # print(get_all())
