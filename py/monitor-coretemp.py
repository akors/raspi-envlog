#!/usr/bin/env python3

import sys
import time
import signal
import argparse

# https://github.com/nicmcd/vcgencmd
import vcgencmd

def sighandler_int(signum, frame):
    print("Received SIGINT, Goodbye!", file=sys.stderr)
    sys.exit()

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

    args = parser.parse_args()

    # Gracefully shut down on signal
    signal.signal(signal.SIGINT, sighandler_int)

    while True:
        print("{}\t{}".format(time.time(), vcgencmd.measure_temp()))
        time.sleep(args.interval)
