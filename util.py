#!/usr/bin/env python3

"""
log parsing utility v1.02: Python CLI application that will parse logs of various kinds.
If FILE is omitted, standard input is used instead.
If multiple options are used at once, the result is the intersection of their
results. The result (matching lines) is printed to standard output.
"""

#Example supported usage:
# ------------------------
# ./util.py -h
# <prints help>
#
# cat test_0.log | ./util.py --first 10
# <prints the first 10 lines of test_0.log>
#
# ./util.py -l 5 test_1.log
# <prints the last 5 lines of test_1.log>
#
# ./utils.py --timestamps test_2.log
# <prints any lines from test_2.log that contain a timestamp>
#
# ./util.py --ipv4 test_3.log
# <prints any lines from test_3.log that contain an IPv4 address>
#
# ./util.py --ipv6 test_4.log
# <prints any lines from test_4.log that contain an IPv6 address>
#
# ./util.py --ipv4 --last 50 test_5.log
# <prints any of the last 50 lines from test_5.log that contain an IPv4 address>

import argparse
import io
import re
import sys

from file_read_backwards import FileReadBackwards


RE_TIMESTAMP = r'(0\d|1\d|[0-2][0-3])(:[0-5]\d){2}'
RE_IPV4 = r'((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.){3}(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])'
RE_IPV6 = r'([\dA-Fa-f]{4}\:){7}[\dA-Fa-f]{4}'


def match_timestamp(line):
    # Return True when matches timestamp in format 'HH:MM:SS'
    if re.findall(RE_TIMESTAMP, line):
        return True
    return False


def match_ipv4(line):
    if re.findall(RE_IPV4, line):
        return True
    return False


def match_ipv6(line):
    if re.findall(RE_IPV6, line):
        return True
    return False


def apply_filters(line, filter_funcs):

    for f in filter_funcs:
        if f(line):
            continue
        else:
            return False
    else:
        return True


def run(argv=[], stdin=None):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('file', metavar='FILE', nargs='?', default=None, help='log filename')
    parser.add_argument('-f', '--first', metavar='NUM', type=int, help='Print first NUM lines')
    parser.add_argument('-l', '--last', metavar='NUM', type=int, help='Print last NUM lines')
    parser.add_argument('-t', '--timestamps', action='store_true', help='Print lines that contain a timestamp in HH:MM:SS format')
    parser.add_argument('-i', '--ipv4', action='store_true', help='Print lines that contain an IPv4 address')
    parser.add_argument('-I', '--ipv6', action='store_true', help='Print lines that contain an IPv6 address (standard notation)')
    args = parser.parse_args(args=argv)

    filters = []
    if args.timestamps:
        filters.append(match_timestamp)
    if args.ipv4:
        filters.append(match_ipv4)
    if args.ipv6:
        filters.append(match_ipv6)

    if args.file:
        if args.first:
            with io.open(args.file) as fin:
                for i in range(0, args.first):
                    if fin.readable():
                        line = fin.readline()
                        if apply_filters(line, filters):
                            sys.stdout.write(line)
                    else:
                        break
        elif args.last:
            buffer = []
            # Optimization for lage files - read from the end:
            with FileReadBackwards(args.file) as fin:
                for i in range(0, int(args.last)):
                    line = fin.readline()
                    if line:
                        buffer.append(line)
                    else:
                        break
            for l in reversed(buffer):
                if apply_filters(l, filters):
                    sys.stdout.write(l)
        else:
            with open(args.file) as fin:
                for line in fin:
                    if apply_filters(line, filters):
                        sys.stdout.write(line)

    else:
        # Assume log content in stdin.
        buffer = stdin.readlines()
        lines = []
        if args.first:
            lines = buffer[0:args.first]
        elif args.last:
            if args.last > len(buffer):
                lines = buffer
            else:
                lines = buffer[len(buffer) - args.last: len(buffer)]
        else:
            lines = buffer
        for l in lines:
            if apply_filters(l, filters):
                sys.stdout.write(l)


if __name__ == '__main__':
    run(sys.argv[1:], stdin=sys.stdin)
