import json
import copy

import random_data

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


class TimelineLine:
    """
    REUSED CODE
    Generated by ChatGPT, verified by Yellow Fox
    """

    def __init__(self, title, css):
        self.title = title
        self.css = css
        self.events = []

    def to_dict(self):
        return {
            "title": self.title,
            "css": self.css,
            "events": [x.to_dict() for x in self.events]
        }


class TimelineEvent:
    current_id = 1

    def __init__(self, time, title, event_type="", status="", description=""):
        self.id = TimelineEvent.current_id
        TimelineEvent.current_id += 1
        self.time = time
        self.title = title
        self.event_type = event_type
        self.status = status
        self.description = description

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.event_type,
            "time": self.time,
            "title": self.title,
            "status": self.status,
            "description": self.description
        }

    @classmethod
    def reset_id(cls):
        cls.current_id = 1


def init_device():
    return copy.deepcopy(device)


def init_router():
    return copy.deepcopy(router)


if __name__ == "__main__":
    # device0 = init_device()
    # device0["mac"] = random_data.random_mac()
    # device0["ip"] = random_data.random_ip()

    # router0 = init_router()
    # router0["name"] = "Test MikroTik"
    # router0["networks"].append("192.168.1.1")
    # router0["offenses"] = 0
    # router0["devices"].append(device0)

    # print(json.dumps(router0, indent=4))

    line = TimelineLine('Events', 'events')

    line.events.append(TimelineEvent(92000, "Start Work"))
    line.events.append(TimelineEvent(93000, "End Work", "end_work", "complete", "Finished work for the day."))

    serialized_line = json.dumps(line.to_dict())
    print(serialized_line)

    TimelineEvent.reset_id()
    event_separate = TimelineEvent(92000, "Why do I bother...")
    print(json.dumps(event_separate.to_dict()))
