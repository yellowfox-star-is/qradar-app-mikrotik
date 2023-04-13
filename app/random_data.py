import random


# REUSED CODE
# Generated by ChatGPT, verified by YellowFox
# Function to generate a random MAC address of Raspberry Pi
def random_mac():
    # Raspberry Pi MAC address prefix
    mac_prefix = 'b8:27:eb'

    # Generate random bytes for the remaining 3 octets
    mac_octets = [random.randint(0x00, 0xff) for _ in range(3)]

    # Format the MAC address as a string
    mac_address = mac_prefix + ':' + ':'.join([format(b, '02x') for b in mac_octets])

    return mac_address


# REUSED CODE
# Generated by ChatGPT, verified by YellowFox
# Function to generate a random IP address from LAN network
def random_ip():
    # Example LAN subnet: 192.168.1.x
    subnet = "192.168.1."

    # Generate a random value for 'x'
    random_ip = subnet + str(random.randint(1, 254))

    return random_ip
