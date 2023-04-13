import base64
import copy
import json
import logging
import time
import re
import datetime

from qpylib import qpylib
import requests

import objects, search
from operations import *

event_source_type_name = "Mikrotik RouterOS"

ip4_empty = ['0.0.0.0']
ip6_empty = ['0:0:0:0:0:0:0:0']
mac_empty = ['00:00:00:00:00:00']
all_empty = ip4_empty + ip6_empty + mac_empty

default_ariel_days = 31
days_extend = 10
seconds_in_day = 86400
milliseconds_in_day = seconds_in_day * 1000

VERIFY = False
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


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


def get_routers():
    # get response
    event_source_id = get_event_source_type_id()
    params = {
        "filter": f"type_id={event_source_id}"
    }
    response = qpylib.REST(rest_action="GET",
                           request_url="/api/config/event_sources/log_source_management/log_sources",
                           params=params,
                           verify=VERIFY)

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


def get_networks(router_id):
    # get information in which network can be searched
    network_columns = ['sourceip', 'sourcev6', 'identityip']
    # XXX CRITICAL ariel pulls events also from remote accesses. it should pull in data only from local events
    # change it to device assignments or other local events
    query = f'SELECT {str_with_delimiter(network_columns,",")} FROM events WHERE logsourceid = {router_id} LAST 7 DAYS'
    search_results = search.search(query)

    # parse information into more workable format
    ipv4_source, ipv6_source = sort_ip_addresses(search_results)

    ipv4_source = remove_empty(ipv4_source, all_empty)
    ipv6_source = remove_empty(ipv6_source, all_empty)

    # find a network from ip addresses
    distance = address_distance('192.168.1.250', '192.168.2.250')

    # XXX TODO I should ask overseer, if it is really smart to do this, it could take very long
    # so far have a look on devices and offenses

    return []


def get_offenses(router_id: str):
    params = {
        'filter': f'log_sources contains id={router_id} and status="OPEN"'
    }
    response = qpylib.REST(rest_action='GET',
                           request_url='/api/siem/offenses',
                           params=params,
                           verify=VERIFY)
    data = response.json()

    return data


def get_devices(router_id: str):
    assigned_event_qid = get_qid_record_id("Assigned IP Address")
    deassgined_event_qid = get_qid_record_id("Deassigned IP Address")
    days = 0

    while True:
        days, is_max = extend_time(router_id, days)
        query = search.search(f'SELECT sourcemac, sourceip, sourcev6, eventid, qid '
                              f'FROM events '
                              f'WHERE logsourceid = {router_id} '
                              f'AND ( qid = {assigned_event_qid} '
                              f'OR qid = {deassgined_event_qid} ) '
                              f'ORDER BY startTime DESC '
                              f'LAST {days} DAYS')

        if is_max and len(query) == 0:
            return []
        if len(query) != 0:
            break
        # Extend Search

    devices = []
    completed_list = []
    for event in query:
        event_qid = event['qid']
        event_mac = event['sourcemac']
        event_add = pick_nonempty_addresses([event['sourceip'], event['sourcev6']])

        # IF BROKEN RECORD
        if event_mac in mac_empty:
            # TODO XXX Need to somehow notify the user, that they have broken records.
            # Technically, this event should have both sourcemac and source IP.
            # So if none are here, DSM module might be broken.
            continue

        if event_mac in completed_list:
            continue

        if event_qid == deassgined_event_qid:
            completed_list.append(event_mac)
            continue

        if event_qid == assigned_event_qid:
            device = objects.init_device()
            device['mac'] = event_mac
            device['ip'] = event_add

            devices.append(device)

            completed_list.append(event_mac)

            continue

        raise NotImplementedError(f"Received unexpected event qid: {event_qid}")

    return devices


def get_raw(router_id, starttimestamp=None, endtimestamp=None):
    query = f'SELECT starttime, endtime, payload '\
            f'FROM events WHERE logsourceid = {router_id} '

    if starttimestamp is None and endtimestamp is None:
        search_days = default_ariel_days
    elif starttimestamp is not None and endtimestamp is not None:
        search_days = days_in_past(starttimestamp)
        query += f'AND ({starttimestamp} < starttime AND startTime < {endtimestamp}) '
    else:
        raise NotImplementedError(f"Unexpected calling of get_raw: "
                                  f"router_id={router_id}, "
                                  f"starttimestamp={starttimestamp}, "
                                  f"endtimestamp={endtimestamp}")

    query += f'ORDER BY startTime DESC '\
             f'LAST {search_days} DAYS'

    result = search.search(query)

    if result is None:
        return []

    payloads = process_payloads(result)
    copy_from_dict_to_dict(result, payloads, 'starttime', 'timestamp')

    return payloads


def populate_qid(payloads):
    resolved_qids = {}
    for i in range(len(payloads)):
        qid = payloads[i]['qid']

        if qid not in resolved_qids:
            qid_record = get_gid_record(qid)
            resolved_qids[qid] = copy.deepcopy(qid_record)

        payloads[i]['name'] = resolved_qids[qid]['name']
        payloads[i]['description'] = resolved_qids[qid]['description']


def get_timeline(router_id, start_timestamp=None, end_timestamp=None):
    query = f'SELECT starttime, endtime, qid, payload FROM events ' \
            f'WHERE logsourceid = {router_id} ' \

    if start_timestamp is None and end_timestamp is None:
        search_days = default_ariel_days
        end_timestamp = int(time_ms())
        start_timestamp = end_timestamp - search_days * milliseconds_in_day
    elif start_timestamp is not None and end_timestamp is not None:
        search_days = days_in_past(start_timestamp)
        query += f'AND ({start_timestamp} < startTime AND startTime < {end_timestamp}) '

    query += f'ORDER BY startTime DESC LAST {search_days} DAYS'

    result = search.search(query)

    if result is None:
        return []

    payloads = process_payloads(result)
    copy_from_dict_to_dict(result, payloads, 'starttime', 'timestamp')
    copy_from_dict_to_dict(result, payloads, 'qid')
    populate_qid(payloads)

    offenses = get_offenses(router_id)

    formatted_timeline = format_to_timeline(start_timestamp, end_timestamp, payloads, offenses)

    return formatted_timeline


def format_to_timeline(start_timestamp, end_timestamp, payloads, offenses):
    line_events = objects.TimelineLine('Events', 'events')
    line_events.events = [objects.TimelineEvent(n['timestamp'], n['payload']) for n in payloads]

    objects.TimelineEvent.reset_id()
    line_offenses = objects.TimelineLine('Offenses', 'offenses')
    line_offenses.events = [objects.TimelineEvent(n['start_time'], n['description']) for n in offenses]

    data = {
        "start_time": start_timestamp,
        "stop_time": end_timestamp,
        "lines": [line_events.to_dict(), line_offenses.to_dict()]
    }

    return data


def make_id(object):
    jsonstring = json.dumps(object)
    h = fnv1a_128(jsonstring.encode())
    unformatted_hex = h.hex()
    formatted_hex = '-'.join(re.findall('.{4}', unformatted_hex))
    return formatted_hex


def get_qid_record_id(qid_name: str):
    params = {
        'filter': f'name="{qid_name}"',
        'Range': 'item=0-49'
    }
    response = qpylib.REST(rest_action='GET',
                           request_url='/api/data_classification/qid_records',
                           params=params,
                           verify=VERIFY)
    data = response.json()

    if len(data) > 1:
        logging.warning(f"Received more qid records than expected:\n {data}")
    if len(data) == 0:
        logging.error("Didn't receive any qid in API call.")

    return data[0]['qid']


def get_gid_record(qid):
    params = {
        'filter': f'qid="{qid}"',
        'Range': 'item=0-49'
    }
    response = qpylib.REST(rest_action='GET',
                           request_url='/api/data_classification/qid_records',
                           params=params,
                           verify=VERIFY)
    data = response.json()
    return data[0]


def pick_nonempty_addresses(addresses):
    legit = []
    for address in addresses:
        if address not in all_empty:
            legit.append(address)
    return legit


def get_event_source_type_id():
    # get response
    params = {
        'filter': f'name="{event_source_type_name}"',
        'Range': 'items=0-49'
    }
    response = qpylib.REST(rest_action='GET',
                           request_url='/api/config/event_sources/log_source_management/log_source_types',
                           params=params,
                           verify=VERIFY)

    # parse response
    data = response.json()

    # there should be only one log source type of this name
    if len(data) > 1:
        raise NotImplementedError(f'Got more than one Log Source type of name: "{event_source_type_name}".')
    return data[0]["id"]


def get_logsource(logsource_id):
    response = qpylib.REST(rest_action="GET",
                           request_url=f'/api/config/event_sources/log_source_management/log_sources/{logsource_id}',
                           verify=VERIFY)

    data = response.json()

    return data


def extend_time(router_id, prev_time=0):
    """
    Function that extends number of days to search, up to creation date of router.
    :param router_id: Log source id of router.
    :param prev_time: Optional. Number of days previously used.
    :return: int, boolean: number of days, if it is max time
    """
    if prev_time == 0:
        return default_ariel_days, False

    router = get_logsource(router_id)

    new_days = prev_time + days_extend

    # XXX CRITICAL Changed time getter, need to check this works alright!
    curr_time = int(time_ms())
    creation_time = router['creation_date'] / 1000  # the time is in milliseconds since epoch
    search_time = curr_time - new_days * milliseconds_in_day

    if search_time < creation_time:
        time_diff = curr_time - creation_time
        days_diff = int(time_diff / milliseconds_in_day)
        return days_diff, True

    return new_days, False


def remove_empty(in_list, empty_examples):
    result_list = []
    for item in in_list:
        # isn't in list
        if is_not_in(item, empty_examples):
            result_list.append(item)
    return result_list


# REUSED CODE
# Co-developed by ChatGPT and YellowFox
#
# This function takes a list of dictionaries containing IP addresses as input,
# and sorts them into IPv4 and IPv6 addresses, returning them as two lists.
def sort_ip_addresses(ip_list):
    ipv4_addresses, ipv6_addresses = [], []
    for ip_dict in ip_list:
        for ip_address in ip_dict.values():
            ip_type = check_ip_address(ip_address)
            if ip_type == 'ipv6':
                ipv6_addresses.append(ip_address)
            elif ip_type == 'ipv4':
                ipv4_addresses.append(ip_address)
            else:
                raise NotImplementedError(f"{ip_address} is not a valid IPv4 or IPv6 address")
    return ipv4_addresses, ipv6_addresses


def address_distance(ip_address1, ip_address2):
    ip_add1_number = int(ipaddress.ip_address(ip_address1))
    ip_add2_number = int(ipaddress.ip_address(ip_address2))

    differing_bit_position = highest_differing_bit(ip_add1_number, ip_add2_number)

    return differing_bit_position


def copy_from_dict_to_dict(dict1, dict2, key1, key2=None):
    if len(dict1) != len(dict2):
        raise NotImplementedError('Dictionary length is not same')
    if key2 is None:
        key2 = key1
    length = len(dict1)
    for i in range(length):
        dict2[i][key2] = copy.deepcopy(dict1[i][key1])


# REUSED CODE
# co-developed by ChatGPT and Yellow Fox
# function that decodes payloads, searched from ariel databases encoded in base64
# also adds an identifier, so each payload can be identified
# output is saved into a list of dictionaries
def process_payloads(payloads):
    processed_payloads = []
    for event in payloads:
        payload = {
            'payload': base64.b64decode(event["payload"]).decode("utf-8"),
            'id': make_id(str(event['payload']) + str(event['starttime']) + str(event['endtime'])),
        }
        processed_payloads.append(payload)
    return processed_payloads


if __name__ == "__main__":
    # print(make_id(["ksjfnsoejnoisn"]))
    # print(get_gid_record(1002250012))
    print(get_raw(162))
    print(get_raw(162, 1678537616000, 1681227177000))
    print(get_timeline(162))
    # print(json.dumps(get_raw(162), indent=2))
