#!/usr/bin/python3

import argparse
import sys

PATTERN_PHRASE = "Track.ServicePositioning"


def process_MM_line(line, step):
    pos = line[line.find("pos=(") + 5: line.find("), hdg=")]
    lat = pos[0: pos.find(",")]
    lon = pos[pos.find(", ") + 2: -1]
    hdg = line[line.find("hdg=") + 4: line.find(", v=")]
    v = line[line.find("v=") + 2: line.find(" m/s")]

    return "{},245,{},{},0,{},{},10,{}\n".format(step, lon, lat, hdg, v if (v != "nan") else "0", step)


def setup_parser():
    # Setup CLI arguments
    # autopep8: off
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=str, required=True, help='Output TTP file name')
    parser.add_argument("--input", type=str, required=True, help='Input esotrace file name')
    parser.add_argument('--start', type=float, required=False, default=0.0, help='Packed ID of the first message')
    parser.add_argument('--end', type=float, required=False, default=10000.0, help='Packet ID of the last message')
    return parser.parse_args()
    # autopep8: on


args = setup_parser()

input_file = open(args.input, "r")
output_file = open(args.output, "w")

output_file.write("BEGIN:ApplicationVersion=TomTom Positioning 0.1\n")
output_file.write("0.0,245,SENSOR=GPS\n")

current_step = 1
for line in input_file:
    if PATTERN_PHRASE in line:

        packet_id = float(line[0:line.find(" ")])

        if packet_id > args.end:
            break
        if packet_id < args.start:
            continue

        output_file.write(process_MM_line(line, current_step))
        current_step = current_step + 1
