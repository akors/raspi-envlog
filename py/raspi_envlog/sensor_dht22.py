
from dataclasses import dataclass
from typing import Tuple

import math
import datetime
import configparser
import json

import board
import adafruit_dht

# Initial the dht device, with data pin connected to:
dhtDevice = adafruit_dht.DHT22(board.D4)


class Sensor:
    def __init__(self, config: configparser.ConfigParser):
        # read device configuration
        self.__devices = json.loads(config["sensor_dht22"].get("devices"))

        # convert pin to adafruit_dht device object
        for sn, pin in self.__devices.items():
            adafruit_pin = getattr(board, pin)
            self.__devices[sn] = adafruit_dht.DHT22(pin=adafruit_pin, use_pulseio=False)

    def measure(self):
        measurements = list()

        for sn, dev in self.__devices.items():
            try:
                temperature = dev.temperature
                humidity = dev.humidity
            except RuntimeError as error:
                # Errors happen fairly often, DHT's are hard to read, just keep going
                print("Failed to read sensor ", sn, ": ", error.args[0])
                continue

            timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

            # Sometimes we get crap values from the sensor. Try to detect these
            # and skip the readings
            if humidity is None or temperature is None or  \
                math.isnan(humidity) or math.isnan(temperature) or humidity > 100.0:
                continue

            measurements.append({
                "measurement": "temperature",
                "time": timestamp,
                "tags" : {
                    "sensor" : "DHT22",
                    "sensor_id" : sn
                },
                "fields": { "value": temperature }
            })

            measurements.append({
                "measurement": "humidity",
                "tags" : {
                    "sensor" : "DHT22",
                    "sensor_id" : sn
                },
                "time": timestamp,
                "fields": { "value": humidity }
            })

        return measurements
