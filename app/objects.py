import json
import copy

from . import random_data

device = {
    "mac": "",
    "ip": ""
}

router = {
    "name": "",
    "networks": [],
    "offenses": "",
    "devices": []
}


def init_device():
    return copy.deepcopy(device)


def init_router():
    return copy.deepcopy(router)


if __name__ == "__main__":
    device0 = init_device()
    device0["mac"] = random_data.random_mac()
    device0["ip"] = random_data.random_ip()

    router0 = init_router()
    router0["name"] = "Test MikroTik"
    router0["networks"].append("192.168.1.1")
    router0["offenses"] = 0
    router0["devices"].append(device0)

    print(json.dumps(router0, indent=4))

