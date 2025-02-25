#!python3

import argparse
import json
import polyline


def setup_parser():
    # Setup CLI arguments
    # autopep8: off
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', '-o', type=str, required=True, help="Output KML file name")
    parser.add_argument('--input', '-i', type=str, required=True, help="Data file with a polyline, post data or response")
    parser.add_argument('--leg', '-l', type=int, default=-1, help="By default take all the legs, number is zero-based")
    parser.add_argument('--route', '-r', type=int, default=0, help="In case there are multiple routes")
    args = parser.parse_args()

    return args

args = setup_parser()

def encoded_to_supportingPoints(data):
    polyline_data = data["encodedPolyline"]
    polyline_precision = data["encodedPolylinePrecision"]
    decoded = polyline.decode(polyline_data, polyline_precision)
    converted_coordinates = [{"latitude": lat, "longitude": lon} for lat, lon in decoded]
    return converted_coordinates

with open(args.input) as json_file:
    data = json.load(json_file)
    output_file = open(args.output, "w+")

    if "legs" in data:
            for leg in data["legs"]:
                if "encodedPolyline" in leg:
                    leg["supportingPoints"] = encoded_to_supportingPoints(leg)
                    leg.pop("encodedPolyline")
                    leg.pop("encodedPolylinePrecision")
    else:
        if "encodedPolyline" in data:
            data["supportingPoints"] = encoded_to_supportingPoints(data)
            data.pop("encodedPolyline")
            data.pop("encodedPolylinePrecision")

    json.dump(data, output_file, indent=2)