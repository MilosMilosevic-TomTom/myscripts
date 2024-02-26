#!/usr/bin/python3

import argparse
import sys
import re

SEPARATOR = "\n\n----------------------------------------------------------------\n\n\n"
ONLINE_REQ_REGEX = "SendOnlineRequest.*Route/"
RECEIVING_ROUTE_REGEX = "Receiving \d* online route"
RESOLVING_FAILED_PHRASE = "Polyline resolving failed for route"
LOG_ROUTE_SUMMART_PHRASE = "LogRouteSummary"

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
last_route_summary = None
cnt = 0

for line in input_file:
  if re.search(ONLINE_REQ_REGEX, line, re.IGNORECASE):
    last_request = line
  elif re.search(RECEIVING_ROUTE_REGEX, line, re.IGNORECASE):
    last_id = line
  elif LOG_ROUTE_SUMMART_PHRASE in line:
    last_route_summary = line
  elif RESOLVING_FAILED_PHRASE in line:
    if not(last_request and last_id and last_route_summary):
      print("Some of the failures not paired properly, the log format might have changed")

    output_file.write(last_request)
    output_file.write(last_route_summary)
    output_file.write(last_id)
    output_file.write(line)
    output_file.write(SEPARATOR)

    last_request = None
    last_id = None
    last_route_summary = None

    cnt = cnt + 1

print("Detected {} polyline resolvings failed".format(cnt))