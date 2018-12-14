
from typing import Tuple

import math
import datetime
import configparser
import json

import Adafruit_DHT

# https://github.com/nicmcd/vcgencmd
import vcgencmd

class Sensor:
    def __init__(self, config: configparser.ConfigParser):
        self.__devices = json.loads(config["sensor_dht22"].get("devices"))

    def measure(self):
        measurements = list()

        for sn, pin in self.__devices.items():
            (humidity, temperature) = Adafruit_DHT.read_retry(
                Adafruit_DHT.AM2302,
                pin,
                retries=5,
                delay_seconds=2.5)
            timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

            # Sometimes we get crap values from the sensor. Try to detect these
            # and skip the readings
            if math.isnan(humidity) or math.isnan(temperature) or humidity > 100.0:
                continue

            measurements.append({
                "measurement": "temperature",
                "time": timestamp,
                "tags" : {
                    "sensor" : "DHT22",
                    "sensor_id" : sn
                },
                "fields": { "value": int(temperature*10+.5)/10 }
            })

            measurements.append({
                "measurement": "humidity",
                "tags" : {
                    "sensor" : "DHT22",
                    "sensor_id" : sn
                },
                "time": timestamp,
                "fields": { "value": int(humidity*10+.5)/10 }
            })

        return measurements
