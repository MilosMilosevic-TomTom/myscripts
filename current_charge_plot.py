#!/usr/bin/python3

import argparse
import matplotlib.pyplot as plt
import matplotlib.dates
import math
import re

from datetime import datetime

UPDATE_VEHICLE_REGEX = r'VehicleServiceProto::updateVehicle()'
POS_REGEX = r'NullMapMatcherImpl.cpp:437'
DATATIME_FORMAT = '%d.%m.%Y %H:%M:%S.%f'

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
  return R * c

def setup_parser():
    # Setup CLI arguments
    # autopep8: off
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help='Input esotrace file name')
    parser.add_argument('--start', type=float, required=False, default=0.0, help='Packed ID of the first message')
    parser.add_argument('--end', type=float, required=False, default=10000.0, help='Packet ID of the last message')
    parser.add_argument('--with-timeline', action='store_true', dest='timeline')
    parser.add_argument('--with-packet-id', action='store_true', dest='packet', default=True)
    return parser.parse_args()
    # autopep8: on


args = setup_parser()
use_timeline = args.timeline
use_packet = args.packet
input_file = open(args.input, "r")

xpoints = []
ypoints = []
dis = []
cnt = []
last_coord = []
cum_dist = 0.0
all_cum_dist = 0.0
cons = []
last_charge = None

steps = 0
for line in input_file:
  try:
    packet_id = float(line[0:line.find(" ")])
    rem = int(line[line.find(".")+1:line.find(" ")])
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
      charge = float(line[line.find('current_charge_in_kwh: ')+23:line.find(' max_charge_in_kwh:')])
      ypoints.append(charge)
      cnt.append(int(packet_id)+rem*1.0/100000)
      if last_charge is not None and cum_dist != 0.0:
        print(last_charge-charge)
        print(cum_dist)
        consum = (last_charge-charge)/cum_dist*100
        print("const = {} kWh/100km\n".format(consum))
        cons.append(consum)

      dis.append(cum_dist)
      all_cum_dist = all_cum_dist + cum_dist
      cum_dist = 0.0
      last_charge = charge
    except Exception as e:
      print("Failed converting the string {} to float, dropping the update request".format(charge))
      if len(xpoints) > 0:
        xpoints.pop()
      steps = steps - 1
  elif re.search(POS_REGEX, line):
    lat = float(line[line.find("longitude=")+10:line.find(",raw latitude")])
    lon = float(line[line.find("latitude=")+9:line.find(",on road")])

    if last_coord != []:
      cum_dist = cum_dist + calculate_distance(lat, lon, last_coord[0], last_coord[1])

    last_coord = [lat, lon]

if use_timeline:
  dates = matplotlib.dates.date2num(xpoints)
  plt.plot_date(dates, ypoints)
elif use_packet:
  plt.plot(cnt, ypoints)
else:
  plt.plot(range(steps), ypoints)

changes = []
for i in range(len(ypoints) - 1):
  changes.append(ypoints[i+1] - ypoints[i])

print(max(changes))

if use_timeline:
  ax = plt.gca()
  myFmt = matplotlib.dates.DateFormatter('%H:%M:%S')
  ax.xaxis.set_major_formatter(myFmt)

plt.xlabel(f"PacketId")
plt.ylabel(f"Charge [kWh]")
plt.title(f"Esotrace battery charge over time")
plt.show()

no_noise = []
for a in cons:
  if a < 100.0:
    no_noise.append(a)

plt.figure(2)
plt.plot(no_noise)
plt.ylabel(f"Consumption [kWh/100km]")
plt.title(f"Consumption")
plt.show()

print("Average: {}".format((ypoints[0] - ypoints[-1])/all_cum_dist*100))