#!/usr/bin/python3

import argparse
import matplotlib.pyplot as plt
import matplotlib.dates
import re

from datetime import datetime

UPDATE_VEHICLE_REGEX = r'VehicleServiceProto::updateVehicle()'
DATATIME_FORMAT = '%d.%m.%Y %H:%M:%S.%f'

def setup_parser():
    # Setup CLI arguments
    # autopep8: off
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help='Input esotrace file name')
    parser.add_argument('--start', type=float, required=False, default=0.0, help='Packed ID of the first message')
    parser.add_argument('--end', type=float, required=False, default=10000.0, help='Packet ID of the last message')
    parser.add_argument('--with-timeline', action='store_true', dest='timeline')
    return parser.parse_args()
    # autopep8: on


args = setup_parser()
use_timeline = args.timeline
input_file = open(args.input, "r")

xpoints = []
ypoints = []

steps = 0
for line in input_file:
  try:
    packet_id = float(line[0:line.find(" ")])
  except ValueError:
    continue

  if packet_id > args.end:
      break
  if packet_id < args.start:
      continue

  if re.search(UPDATE_VEHICLE_REGEX, line):
    if use_timeline:
      try:
        # Try to extract the timestamp
        ts_str = line[line.find("--")+2:line.find("PrivacyFlags")]
        ts = datetime.strptime(ts_str.strip().rstrip(), DATATIME_FORMAT)
        xpoints.append(ts)
      except Exception as e:
        # On first failure, fallback to simple points
        print("Failed converting the string {} to datetime, falbacking to usign simple steps as x axis".format(ts_str))
        use_timeline = False
    steps = steps + 1

    try:
      charge = line[line.find('current_charge_in_kwh: ')+23:line.find(' max_charge_in_kwh:')]
      ypoints.append(float(charge))
    except Exception as e:
      print("Failed converting the string {} to float, dropping the update request".format(charge))
      if len(xpoints) > 0:
        xpoints.pop()
      steps = steps - 1


if use_timeline:
  dates = matplotlib.dates.date2num(xpoints)
  plt.plot_date(dates, ypoints)
else:
  plt.plot(range(steps), ypoints)

if use_timeline:
  ax = plt.gca()
  myFmt = matplotlib.dates.DateFormatter('%H:%M:%S')
  ax.xaxis.set_major_formatter(myFmt)

plt.xlabel(f"Timestamp")
plt.ylabel(f"Charge [kWh]")
plt.title(f"Esotrace battery charge over time")
plt.show()
