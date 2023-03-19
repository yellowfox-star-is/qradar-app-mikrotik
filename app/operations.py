import copy
import ipaddress


def str_with_delimiter(list0, delimiter):
    return str(delimiter).join(str(x) for x in list0)


# returns True if item is not in list, returns False if is
def is_not_in(item, list):
    return list.count(item) == 0


# REUSED CODE
# Generated by ChatGPT, verified by YellowFox
# takes a list of strings
# returns a dictionary with the strings as keys and empty lists as values
def create_dictionary(strings, init_value):
    result = {}
    for s in strings:
        result[s] = copy.deepcopy(init_value)
    return result


# REUSED CODE
# Generated by ChatGPT, verified by YellowFox
# returns "ipv4", "ipv6" or None depending on the address format
def check_ip_address(address):
    try:
        ipaddress.IPv4Address(address)
        return "ipv4"
    except ipaddress.AddressValueError:
        pass

    try:
        ipaddress.IPv6Address(address)
        return "ipv6"
    except ipaddress.AddressValueError:
        pass

    return None


def highest_power_of_two(n):
    power = 1
    while power < n:
        power <<= 1
    if power > n:
        power >>= 1
    return power


def highest_differing_bit(n1: int, n2: int):
    mask = ~0
    position = 0
    # XXX CRITICAL this is very dangerous, should be replaced with for loop
    # can fail on overflow
    while True:
        if mask & n1 == mask & n2:
            return position
        position += 1
        mask <<= 1
    return position
