
import configparser
import datetime
from typing import Tuple

import icmplib


THISCONF = 'sensor_ping'

class Sensor:
    def __init__(self, config: configparser.ConfigParser):
        self.destinations = [t.strip() for t in config[THISCONF]['destinations'].split(',')]
        pass

    def measure(self):
        replies = icmplib.multiping(self.destinations, count=10, interval=1, privileged=False)
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()


        measurements = list()
        for dest, reply in zip(self.destinations, replies):
            measurements.extend([
                {
                    "measurement": "ping_avg_rtt",
                    "time": timestamp,
                    "tags": { "dest" : dest },
                    "fields": { "value": reply.avg_rtt }
                },
                {
                    "measurement": "ping_jitter",
                    "time": timestamp,
                    "tags": { "dest" : dest },
                    "fields": { "value": reply.max_rtt }
                },
                {
                    "measurement": "ping_packet_loss",
                    "time": timestamp,
                    "tags": { "dest" : dest },
                    "fields": { "value": reply.packet_loss }
                }
        ])

        return measurements


