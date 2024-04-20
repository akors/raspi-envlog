
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
        clock_core = vcgencmd.measure_clock("core")
        clock_arm = vcgencmd.measure_clock("arm")
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        measurements = list()
        measurements.append({
            "measurement": "coretemp",
            "time": timestamp,
            "fields": { "value": coretemp }
        })

        measurements.append({
            "measurement": "clock_core",
            "time": timestamp,
            "fields": { "value": clock_core }
        })

        measurements.append({
            "measurement": "clock_arm",
            "time": timestamp,
            "fields": { "value": clock_arm }
        })

        return measurements
