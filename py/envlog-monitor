#!/usr/bin/env python3

import sys
import signal
import configparser
import threading

from influxdb import InfluxDBClient

from raspi_envlog import sensor_coretemp
from raspi_envlog import sensor_dht22

THISCONF = 'monitor'
CONFIGPATH = '/etc/raspi-envlog.conf'

config = configparser.ConfigParser(interpolation=None)

# default config values

config['db'] = {
  'host': "localhost",
  'port': "8086",
  'database': "envlog",
  # 'user' : 'root',
  # 'password' : 'root'
}

config[THISCONF] = {
    'interval': 60
}

GPIO_PIN_DHT22 = 17

# waiting on this event to exit
exit_event = threading.Event()


def shutdown_handler(signum, frame):
    print("Received %s, shutting down..." % signal.Signals(signum).name, file=sys.stderr)
    exit_event.set()


def float_positive(value_str):
    float_positive = float(value_str)
    if float_positive <= 0:
         raise argparse.ArgumentTypeError("%s is not a positive value" % value_str)
    return float_positive


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-n', '--interval', dest='interval',
                        action='store', type=float_positive,
                        help='Logging interval in seconds')
    parser.add_argument('-c', '--config', dest='configfile',
                        action='store', type=str, default=CONFIGPATH,
                        help='Config file location')

    parser.add_argument('--sd_notify', action='store_true')

    args = parser.parse_args()

    with open(args.configfile, 'rt') as configfile:
        # read config from file
        config.read_file(configfile, source=args.configfile)

    interval = args.interval if args.interval is not None else config.getfloat(THISCONF, 'interval')

    # Register handlers for Gracefully shut down on signal
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGHUP, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    dbclient = InfluxDBClient(
        config['db']['host'],
        config.getint('db', 'port'),
        config['db']['username'],
        config['db']['password'],
        config['db']['database'])

    #dbclient.create_database(config['db']['database'])
    print("Database connection established.", file=sys.stderr)

    dht22_sensor = sensor_dht22.Sensor(config)
    core_sensor = sensor_coretemp.Sensor(config)

    # if requested, signal to systemd that startup has succeeded
    sd_notifier = None
    if args.sd_notify:
        import sdnotify
        sd_notifier = sdnotify.SystemdNotifier()
        sd_notifier.notify("READY=1")

    while not exit_event.is_set():
        points = list()

        points.extend(core_sensor.measure())
        points.extend(dht22_sensor.measure())

        # writeout to database
        dbclient.write_points(points)

        # Set systemd status if requested
        if sd_notifier is not None:
            sd_notifier.notify("STATUS=SoC temp: {} C\nRoom temp: {} C".format(coretemp, room_temp))

        exit_event.wait(interval)
