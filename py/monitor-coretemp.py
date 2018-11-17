#!/usr/bin/env python3

import sys
import time, datetime
import signal
import configparser
import threading

from influxdb import InfluxDBClient

# https://github.com/nicmcd/vcgencmd
import vcgencmd


THISCONF = 'monitor-coretemp'
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


    args = parser.parse_args()
    
    with open(args.configfile, 'rt') as configfile:
        # read config from file
        config.read_file(configfile, source=CONFIGPATH)
    
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
        
    dbclient.create_database(config['db']['database'])
    print("Database connection established.", file=sys.stderr)

    # prepare points struct. Instead of creating a new one, we will be reusing this
    points = [{
        "measurement": "coretemp",
        "time": None,
        "fields": { "value": None }
    }]
    
    while not exit_event.is_set():
        points[0]["time"] = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat()
        points[0]["fields"]["value"] = vcgencmd.measure_temp()
        dbclient.write_points(points)
        exit_event.wait(interval)


