#!/usr/bin/python3

import argparse
import matplotlib.pyplot as plt
import re

PATTERN_PHRASE = r"route_impl.cpp:469: OnPositionUpdate: progress Progress\("

def setup_parser():
    # Setup CLI arguments
    # autopep8: off
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help='Input esotrace file name')
    parser.add_argument('--start', type=float, required=False, default=0.0, help='Packed ID of the first message')
    parser.add_argument('--end', type=float, required=False, default=10000.0, help='Packet ID of the last message')
    parser.add_argument('--remaining', action='store_true', dest='remaining', default=False)
    return parser.parse_args()
    # autopep8: on


args = setup_parser()

input_file = open(args.input, "r")

offsets = []
remaining = []
cnt = []

for line in input_file:
  if re.search(PATTERN_PHRASE, line):

    packet_id = float(line[0:line.find(" ")])
    rem = int(line[line.find(".")+1:line.find(" ")])

    last_packet_id = packet_id
    if packet_id > args.end:
        break
    if packet_id < args.start:
        continue

    search = re.search(PATTERN_PHRASE, line)

    start = search.end()
    end = line.find("cm, remaining traffic length:")
    line = line[start:end]

    offset_start = line.find("offset:") + len("offset:")
    offset_end = line.find(" cm,")

    rem_start = line.find("remaining length:") + len("remaining length:")

    offsets.append(int(line[offset_start:offset_end])/100.0)
    remaining.append(int(line[rem_start:-1])/100.0)
    cnt.append(int(packet_id)+rem*1.0/100000)

if args.remaining:
  plt.plot(cnt, remaining, color='b', label='remaining offset')

plt.plot(cnt, offsets, color='r', label='progress offset')

plt.xlabel(f"Count")
plt.ylabel(f"Length in m")
plt.legend()
plt.show()

