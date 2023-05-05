#!/usr/bin/python3

import argparse
import math
import re
import sys

PATTERN_PHRASE = [r"Track\.MapMatched",
                  r"NullMapMatcherImpl.*OnFeedResult:timestamp",
                  r"Called OnPredictionUpdate with PredictionUpdateResult:.*has raw position, location is \("]


def calculate_distance(latitude1, longitude1, latitude2, longitude2):
    lat1 = math.radians(latitude1)
    long1 = math.radians(longitude1)
    lat2 = math.radians(latitude2)
    long2 = math.radians(longitude2)
    R = 6371
    dlat = lat1 - lat2
    dlong = long1 - long2
    a = math.sin(dlat/2)*math.sin(dlat/2) + math.cos(lat1)*math.cos(lat2) * math.sin(dlong/2)*math.sin(dlong/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c * 1000

def process_MM_line(line, method, last_coord = None):

    if method == 0:
        ts_start = line.find("ts=")
        pos_start = line.find("pos=(")
        hdg_start = line.find("hdg=")

        ts = line[ts_start+3:pos_start-2]
        pos = line[pos_start+5: hdg_start-3]
        lat = float(pos[0: pos.find(",")])
        lon = float(pos[pos.find(", ") + 2: -1])
        hdg = line[hdg_start+4:line.find(",", hdg_start)]

    elif method == 1:
        ts_start = line.find("timestamp=")
        lon_start = line.find(",raw longitude=")
        lat_start = line.find(",raw latitude=")
        lat_end = line.find(",on road=")

        ts = line[ts_start+10:lon_start]
        lon = float(line[lon_start+15:lat_start])
        lat = float(line[lat_start+14:lat_end])
        hdg = 0

    elif method == 2:
        search = re.search(PATTERN_PHRASE[method], line)
        raw = line[search.end():-2]
        sep = raw.find(",")
        lat = raw[0:sep]
        lon = raw[sep+1:-1]
        hdg = 0

    try:
        ts = float(ts)
    except Exception as e:
        ts = 0

    v = 0
    if last_coord != None:
        dt = ts - last_coord[0]
        v = calculate_distance(last_coord[1], last_coord[2], lat, lon) / dt if dt != 0.0 else 0.0

    return ts, lat, lon, hdg, v


def output_ttp(struct, step):
    return "{},245,{},{},0,{},{},10,{}\n".format(step, struct[2], struct[1], struct[3], struct[4], step)

def output_klm(struct):
    return "{},{},0\n".format(struct[2], struct[1])

def setup_parser():
    # Setup CLI arguments
    # autopep8: off
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=str, required=True, help='Output TTP file name')
    parser.add_argument("--input", type=str, required=True, help='Input esotrace file name')
    parser.add_argument('--start', type=float, required=False, default=0.0, help='Packed ID of the first message')
    parser.add_argument('--end', type=float, required=False, default=10000.0, help='Packet ID of the last message')
    parser.add_argument('--kml', action='store_true', dest='kml')
    parser.add_argument('--phrase-index', type=int, default=0, dest='phrase', help='Supported phrases for now ["Track.MapMatched", "NullMapMatcherImpl.*OnFeedResult"]')
    return parser.parse_args()
    # autopep8: on


args = setup_parser()

if args.phrase >= len(PATTERN_PHRASE):
    print("Number of possible phrases is {}, the selected index {} is not possible".format(len(PATTERN_PHRASE), args.phrase))
    exit()

input_file = open(args.input, "r")
output_file = open(args.output, "w")

if args.kml:
    output_file.write('<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n')
    output_file.write('<Style id="l">\n<LineStyle><color>ffff00ff</color>\n<width>4</width>\n</LineStyle>\n<PolyStyle>\n<color>ffff00ff</color>\n</PolyStyle>\n</Style>')
    output_file.write('<Placemark>\n<styleUrl>#l</styleUrl>\n<LineString>\n<coordinates>')
else:
    output_file.write("BEGIN:ApplicationVersion=TomTom Positioning 0.1\n")
    output_file.write("0.0,245,SENSOR=GPS\n")

current_step = 1
struct = None

for line in input_file:
    if re.search(PATTERN_PHRASE[args.phrase], line):

        packet_id = float(line[0:line.find(" ")])
        if packet_id > args.end:
            break
        if packet_id < args.start:
            continue

        struct = process_MM_line(line, args.phrase, struct)
        output_file.write(output_klm(struct) if args.kml else output_ttp(struct, current_step))
        current_step = current_step + 1

if args.kml:
    output_file.write('</coordinates>\n</LineString>\n</Placemark>\n</Document>\n</kml>')

print("Extracted {} coordinates".format(current_step))