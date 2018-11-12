#!/usr/bin/env python3

import sys
import time
import signal
import argparse
import threading

# https://github.com/nicmcd/vcgencmd
import vcgencmd


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
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-n', '--interval', dest='interval',
                        action='store', type=float_positive,
                        default=60,
                        help='Logging interval in seconds. Default is 60.')

    parser.add_argument('outfile', nargs='?', type=argparse.FileType('at'), default=None)

    args = parser.parse_args()

    if args.outfile is None:
        outfile=sys.stdout
    else:
        outfile=args.outfile

    # Gracefully shut down on signal
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGHUP, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    while not exit_event.is_set():
        print("{}\t{}".format(time.time(), vcgencmd.measure_temp()), file=outfile)
        exit_event.wait(args.interval)

