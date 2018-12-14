
import configparser
import datetime
from typing import Tuple

# https://github.com/nicmcd/vcgencmd
import vcgencmd

THISCONF = 'sensor_coretemp'

class Sensor:
    def __init__(self, config: configparser.ConfigParser):
        pass

    def measure(self):
        coretemp = vcgencmd.measure_temp()
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        measurements = list()
        measurements.append({
            "measurement": "coretemp",
            "time": timestamp,
            "fields": { "value": coretemp }
        })

        return measurements
