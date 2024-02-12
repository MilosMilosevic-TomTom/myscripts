#!/usr/bin/python3

import argparse
import sys
import re

SEPARATOR = "\n\n----------------------------------------------------------------\n\n\n"
ONLINE_REQ_REGEX = "SendOnlineRequest.*Route/"
RECEIVING_ROUTE_REGEX = "Receiving.*online route"
RESOLVING_FAILED_PHRASE = "Polyline resolving failed for route"

def setup_parser():
    # Setup CLI arguments
    # autopep8: off
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', '-o', type=str, required=True, help="Output KML file name")
    parser.add_argument('--input', '-i', type=str, required=True, help="Data file with a polyline, post data or response")
    args = parser.parse_args()
    return args
    # autopep8: on

args = setup_parser()

input_file_name = args.input
output_file_name = args.output

print("Checking the failed polyline resolvings and outputing to file {}".format(args.output))

input_file = open(input_file_name, "r")
output_file = open(output_file_name, "w")

last_request = None
last_id = None
cnt = 0

for line in input_file:
  if re.search(ONLINE_REQ_REGEX, line, re.IGNORECASE):
    last_request = line
  elif re.search(RECEIVING_ROUTE_REGEX, line, re.IGNORECASE):
    last_id = line
  elif RESOLVING_FAILED_PHRASE in line:
    output_file.write(last_request)
    output_file.write(last_id)
    output_file.write(line)
    output_file.write(SEPARATOR)
    cnt = cnt + 1

print("Detected {} polyline resolvings failed".format(cnt))