#!/usr/bin/python3

import argparse
import json

def setup_parser():
    # Setup CLI arguments
    # autopep8: off
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", '-o', type=str, required=True, help='Output KML file name')
    parser.add_argument("--input", '-i', type=str, required=True, help='Post data file')
    parser.add_argument('--leg', '-l', type=int, default=-1, help='By default take all the legs, number is zero-based')
    parser.add_argument('--mode', '-m', type=str, default="post", help='Switch between post data and response data')
    return parser.parse_args()
    # autopep8: on

args = setup_parser()

start = '<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document><Folder><Folder><!-- route --><Folder><!-- leg --><Placemark><LineString><coordinates>'
close_line = '</coordinates></LineString></Placemark>'
start_wp = '<Placemark><Point><coordinates>'
end_wp = '</coordinates></Point></Placemark>'
end = '</Folder></Folder></Folder></Document></kml>'


def add_pin(lon, lat, name=None):
    if name is not None:
        return "<Placemark><Point><coordinates>{},{}</coordinates></Point><name>{}</name></Placemark>".format(lon, lat, name)
    else:
        return "<Placemark><Point><coordinates>{},{}</coordinates></Point></Placemark>".format(lon, lat)

with open(args.input) as json_file:
    data = json.load(json_file)
    output_file = open(args.output, "w+")

    leg_limits = [0]

    if args.mode == "response":
        points = []
        try:
            for leg in data["routes"][0]["legs"]:
                points.extend(leg["points"])
                leg_limits.append(leg_limits[-1] + len(leg["points"]) - 1)
        except KeyError as e:
            exit("Input file format wrong, key {} not found" + str(e))

        data["supportingPoints"] = points
    elif args.mode == "post":
        try:
            for w in data["pointWaypoints"]:
                leg_limits.append(w["supportingPointIndex"])
            leg_limits.append(len(data["supportingPoints"]))
        except KeyError as e:
            pass
    else:
        exit("Unknown mode {}, supported modes are 'post' and 'response'".format(args.mode))

    if args.leg > len(leg_limits) - 2:
        exit("Input file contains {} legs while requested leg is {} (zero-based)".format(len(leg_limits)-1, args.leg))

    print(start, file=output_file)

    try:
        if args.leg == -1:
            s = 0
            e = -1
        else:
            s = leg_limits[args.leg]
            e = leg_limits[args.leg+1]
        for p in data["supportingPoints"][s:e]:
            print("{},{}".format(p["longitude"], p["latitude"]), file=output_file)
    except KeyError as e:
        exit("Input file format wrong, key {} not found" + str(e))

    print(close_line, file=output_file)

    print(add_pin(data["supportingPoints"][0]["longitude"], data["supportingPoints"][0]["latitude"], "Start"), file=output_file)
    print(add_pin(data["supportingPoints"][-1]["longitude"], data["supportingPoints"][-1]["latitude"], "End"), file=output_file)

    for cnt, l in enumerate(leg_limits[1:-1]):
        print("Waypoint {}: {},{}".format(cnt+1, data["supportingPoints"][l]["latitude"], data["supportingPoints"][l]["longitude"]))
        print(add_pin(data["supportingPoints"][l]["longitude"], data["supportingPoints"][l]["latitude"], "Waypoint" + str(cnt+1)), file=output_file)

    print(end, file=output_file)
