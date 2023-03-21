import copy
import base64
import logging

import search
import json
import objects
from operations import *
from operations import is_not_in
from qpylib import qpylib

event_source_type_name = "Mikrotik RouterOS"

ip4_empty = ['0.0.0.0']
ip6_empty = ['0:0:0:0:0:0:0:0']
mac_empty = ['00:00:00:00:00:00']
all_empty = ip4_empty + ip6_empty + mac_empty


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


def get_qid_record_id(qid_name: str):
    params = {
        'filter': f'name="{qid_name}"',
        'Range': 'item=0-49'
    }
    response = qpylib.REST(rest_action='GET',
                           request_url='/api/data_classification/qid_records',
                           params=params)
    data = response.json()

    if len(data) > 1:
        logging.warning(f"Received more qid records than expected:\n {data}")
    if len(data) == 0:
        logging.error("Didn't receive any qid in API call.")

    return data[0]['qid']


def get_devices(router_id: str):
    # TODO XXX need to add expendable days, somehow, find what the upper limit is
    days = 31
    assigned_event_qid = get_qid_record_id("Assigned IP Address")
    deassgined_event_qid = get_qid_record_id("Deassigned IP Address")
    query = search.search(f'SELECT sourcemac, sourceip, sourcev6, eventid, qid '
                          f'FROM events '
                          f'WHERE qid = {assigned_event_qid} '
                          f'OR qid = {deassgined_event_qid} '
                          f'ORDER BY startTime DESC '
                          f'LAST {days} DAYS')

    if len(query) == 0:
        return []

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


def pick_nonempty_addresses(addresses):
    legit = []
    for address in addresses:
        if address not in all_empty:
            legit.append(address)
    return legit


def get_offenses(router_id: str):
    params = {
        'filter': f'log_sources contains id={router_id} and status="OPEN"',
        'Range': 'items=0-49'
    }
    response = qpylib.REST(rest_action='GET',
                           request_url='/api/siem/offenses',
                           params=params)
    data = response.json()

    # TODO parse the data more, test when there is an offense

    return data


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


def remove_empty(in_list, empty_examples):
    result_list = []
    for item in in_list:
        # isn't in list
        if is_not_in(item, empty_examples):
            result_list.append(item)
    return result_list


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

    return None


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


# REUSED CODE
# Generated by ChatGPT, Adapted by Yellow Fox
# function that decodes payloads, searched from ariel databases encoded in base64
# output is saved into a list of strings
def decode_payloads(payloads):
    decoded_payloads = []
    for event in payloads:
        payload = base64.b64decode(event["payload"]).decode("utf-8")
        decoded_payloads.append(payload)
    return decoded_payloads
# END OF REUSED CODE


if __name__ == "__main__":
    routers = get_routers()
    print(routers)
    # search_results = search.search(f"SELECT * FROM events LAST 1 HOURS")
    # print(json.dumps(search_results, indent=4))
    # print(get_all())
    devices = get_devices('162')
    print(devices)
