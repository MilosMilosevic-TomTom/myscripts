#!/usr/bin/python3

import argparse
import math
import re
import sys

PATTERN_PHRASE = [r"drivingassistance_adapter.*has matched position", r"MapMatchedResult.*on road"]

def setup_parser():
    # Setup CLI arguments
    # autopep8: off
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help='Input esotrace file name')
    parser.add_argument('--start', type=float, required=False, default=0.0, help='Packed ID of the first message')
    parser.add_argument('--end', type=float, required=False, default=10000.0, help='Packet ID of the last message')
    parser.add_argument('--plot', action='store_true', dest='plot')
    parser.add_argument('--phrase-index', type=int, default=0, dest='phrase', help='Supported phrases for now ["Track.MapMatched", "MapMatchedResult.*OnFeedResult"]')
    return parser.parse_args()
    # autopep8: on


args = setup_parser()

if args.phrase >= len(PATTERN_PHRASE):
    print("Number of possible phrases is {}, the selected index {} is not possible".format(len(PATTERN_PHRASE), args.phrase))
    exit()

input_file = open(args.input, "r")

# List of pairs {start_packet_id, end_packed_id}
on_roads = []
off_roads = []
was_on_road = None
start_packet_id = None
last_packet_id = None
cnt_on_road = 0
cnt_off_road = 0

for line in input_file:
  if re.search(PATTERN_PHRASE[args.phrase], line):

    packet_id = float(line[0:line.find(" ")])
    last_packet_id = packet_id
    if packet_id > args.end:
        break
    if packet_id < args.start:
        continue

    search = re.search(PATTERN_PHRASE[args.phrase], line)
    is_on_road = line[search.end()+1: search.end()+5] == 'true'

    if is_on_road:
      cnt_on_road = cnt_on_road + 1
    else:
      cnt_off_road = cnt_off_road + 1

    if was_on_road == True:
      if not is_on_road:
        on_roads.append({start_packet_id, packet_id})
        was_on_road = None
    elif was_on_road == False:
      if is_on_road:
        off_roads.append({start_packet_id, packet_id})
        was_on_road = None
    else:
      start_packet_id = packet_id
      was_on_road = is_on_road


if was_on_road == True:
  on_roads.append({start_packet_id, last_packet_id})
elif was_on_road == False:
  off_roads.append({start_packet_id, last_packet_id})
else:
  raise ValueError('No position update was found')

changes = len(on_roads) + len(off_roads)

print("On road intervals: {}".format(on_roads))
print("Off road intervals: {}".format(off_roads))

print("Processed {} possitions".format(cnt_on_road + cnt_off_road))
print("Number of changes {} and {}% of possitions were on road".format(changes, cnt_on_road * 100.0 / (cnt_off_road + cnt_on_road)))