"""Relays heart rate from a Pico over USB serial to hr-osc."""

import argparse
import os
import sys
import time
import traceback

import serial

from . import __version__
from .runtime import Log, SingleInstance, default_data_dir
from .serial_source import BAUD, READ_TIMEOUT, find_port, parse_line
from .sink import DEFAULT_URL, HrOscSink

APP = "hr-bridge-pico"
RETRY_SECONDS = 3


def build_parser():
    parser = argparse.ArgumentParser(
        prog=APP,
        description="Relay heart rate from a Raspberry Pi Pico W over USB serial to hr-osc.",
    )
    parser.add_argument("--url", default=DEFAULT_URL, help="hr-osc HTTP receiver (default: %(default)s)")
    parser.add_argument("--port", help="serial port to use instead of detecting the board")
    parser.add_argument("--log", help="log file path (default: bridge.log under the platform data directory)")
    parser.add_argument("--no-log-file", action="store_true", help="log to the console only")
    parser.add_argument("--quiet", action="store_true", help="do not echo the log to the console")
    parser.add_argument("--allow-multiple", action="store_true", help="skip the single-instance check")
    parser.add_argument("--version", action="version", version="%(prog)s " + __version__)
    return parser


def relay(args, log):
    sink = HrOscSink(args.url)
    waiting = False
    while True:
        port = args.port or find_port()
        if not port:
            if not waiting:
                log("waiting for the board")
                waiting = True
            time.sleep(RETRY_SECONDS)
            continue
        waiting = False
        try:
            with serial.Serial(port, BAUD, timeout=READ_TIMEOUT) as connection:
                log("reading " + port)
                fresh = True
                while True:
                    bpm = parse_line(connection.readline())
                    if bpm is None:
                        continue
                    if fresh:
                        log("streaming, first bpm {}".format(bpm))
                        fresh = False
                    sink.send(bpm)
        except serial.SerialException as error:
            log("serial lost: {}".format(error))
            time.sleep(RETRY_SECONDS)


def main(argv=None):
    args = build_parser().parse_args(argv)
    data_dir = default_data_dir(APP)
    log_path = None if args.no_log_file else (args.log or os.path.join(data_dir, "bridge.log"))
    log = Log(log_path, echo=not args.quiet)
    lock = SingleInstance(os.path.join(data_dir, "instance.lock"))
    if not args.allow_multiple and not lock.acquire():
        log("another instance is already running")
        return 0
    log("{} {} start".format(APP, __version__))
    try:
        relay(args, log)
    except KeyboardInterrupt:
        log("stopped")
    except Exception:
        log("fatal:\n" + traceback.format_exc())
        raise
    finally:
        lock.release()
    return 0


if __name__ == "__main__":
    sys.exit(main())
