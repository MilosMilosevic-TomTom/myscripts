#!/usr/bin/python3

import argparse
import json
import matplotlib.pyplot as plt
import numpy as np


from datetime import datetime, timedelta

DATATIME_FORMAT = '%d.%m.%Y %H:%M:%S.%f'

# trip_service messages
CREATING_TRIP_SERVICE = 'Creating trip service core with configuration'
TRIP_SERVICE_START_SUCCESS = 'Trip service startup complete'
TRIP_SERVICE_START_FAIL = 'Failed to start trip service core'

# crashes
CRASH_START = '*** *** *** *** *** *** *** *** *** *** *** *** *** *** *** ***'
CRASH_DEBUG = 'crash.DEBUG'

# navigation_impl messages
PLAN_TRIP_REQUEST = 'Plan Trip request: id '
PLAN_TRIP_RESPONSE = 'Plan Trip response: id '
DELTE_TRIP_REQUEST = 'Delete Trip request: id '
DELETE_TRIP_RESPONSE = ' Delete Trip response: id '
START_NAVIGATION_REQUEST = 'Start Navigation request: id '

# for the futures
CANCEL_TRIP_PLANNING_REQUEST = 'Cancel Trip planning requested ??????'
# errors
PROTOBUF_CHANNEL_INTERUPTED_ERR = 'Protobuf channel interrupted'

EMPTY_TRIP = {'id':None, 'plan':None, 'routes':[], 'created':None, 'response':None, 'navigated':None, 'better_proposals':[], 'deleted':None}
EMPTY_CRASH = {'pid':None, 'tid':None, 'cmd':None, 'stacktrace':'', 'timestamp':None, 'uptime':None, 'tracetime':None}

def setup_parser():
    # Setup CLI arguments
    # autopep8: off
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True, help='Input esotrace file name')
    parser.add_argument('--start', type=float, required=False, default=0.0, help='Packed ID of the first message')
    parser.add_argument('--end', type=float, required=False, default=10000.0, help='Packet ID of the last message')
    return parser.parse_args()
    # autopep8: on

def print_crashes_report(crashes):
  print('Found {} crashes in {} different components'.format(np.sum([len(x) for _, x in crashes.items()]), len(crashes)))
  for cmd, list_of_crashes in crashes.items():
    print("\tComponent: {}", cmd)
    for crash in list_of_crashes:
      print("\t\tTimestamp: {}".format(crash['timestamp']))
      print("\n" + crash['stacktrace'])


def display_major_events(major_events, crashes):
  merged_events = []

  for event_type, events in major_events.items():
    for event in events:
      merged_events.append([event['tracetime'], "Create trip service"])

  for cmd, list_of_crashes in crashes.items():
    for crash in list_of_crashes:
      merged_events.append([crash['tracetime'], "Crash in {}".format(cmd)])

  labels = []
  dates = []

  for event in merged_events:
    labels.append('{0:%H:%m:%S}\n{1}'.format(event[0], event[1]))
    dates.append(event[0])

  min_date = np.min(dates) - timedelta(seconds=15)
  max_date = np.max(dates) + timedelta(seconds=15)

  fig, ax = plt.subplots(figsize=(15, 4), constrained_layout=True)
  _ = ax.set_ylim(-2, 1.75)
  _ = ax.set_xlim(min_date, max_date)
  _ = ax.axhline(0, xmin=0.05, xmax=0.95, c='deeppink', zorder=1)

  _ = ax.scatter(dates, np.zeros(len(dates)), s=120, c='palevioletred', zorder=2)
  _ = ax.scatter(dates, np.zeros(len(dates)), s=30, c='darkmagenta', zorder=3)

  label_offsets = np.zeros(len(dates))
  label_offsets[::2] = 0.35
  label_offsets[1::2] = -0.7
  for i, (l, d) in enumerate(zip(labels, dates)):
      _ = ax.text(d, label_offsets[i], l, ha='center', fontfamily='serif', fontweight='bold', color='royalblue',fontsize=12)

  stems = np.zeros(len(dates))
  stems[::2] = 0.3
  stems[1::2] = -0.3
  markerline, stemline, baseline = ax.stem(dates, stems, use_line_collection=True)
  _ = plt.setp(markerline, marker=',', color='darkmagenta')
  _ = plt.setp(stemline, color='darkmagenta')


  # hide lines around chart
  for spine in ["left", "top", "right", "bottom"]:
      _ = ax.spines[spine].set_visible(False)

  # hide tick labels
  _ = ax.set_xticks([])
  _ = ax.set_yticks([])

  _ = ax.set_title('Major events', fontweight="bold", fontfamily='serif', fontsize=16,
                   color='royalblue')

  plt.show()

def display_plots(trip_data):
  for tid, trip in trip_data.items():
    labels = []
    dates = []

    for key in ['created', 'navigated', 'deleted']:
      if trip.get(key) != None:
        labels.append('{0:%H:%m:%S}\n{1}'.format(trip.get(key), key))
        dates.append(trip.get(key))

    min_date = np.min(dates) - timedelta(seconds=15)
    max_date = np.max(dates) + timedelta(seconds=15)

    fig, ax = plt.subplots(figsize=(15, 4), constrained_layout=True)
    _ = ax.set_ylim(-2, 1.75)
    _ = ax.set_xlim(min_date, max_date)
    _ = ax.axhline(0, xmin=0.05, xmax=0.95, c='deeppink', zorder=1)

    _ = ax.scatter(dates, np.zeros(len(dates)), s=120, c='palevioletred', zorder=2)
    _ = ax.scatter(dates, np.zeros(len(dates)), s=30, c='darkmagenta', zorder=3)

    label_offsets = np.zeros(len(dates))
    label_offsets[::2] = 0.35
    label_offsets[1::2] = -0.7
    for i, (l, d) in enumerate(zip(labels, dates)):
        _ = ax.text(d, label_offsets[i], l, ha='center', fontfamily='serif', fontweight='bold', color='royalblue',fontsize=12)

    stems = np.zeros(len(dates))
    stems[::2] = 0.3
    stems[1::2] = -0.3
    markerline, stemline, baseline = ax.stem(dates, stems, use_line_collection=True)
    _ = plt.setp(markerline, marker=',', color='darkmagenta')
    _ = plt.setp(stemline, color='darkmagenta')


    # hide lines around chart
    for spine in ["left", "top", "right", "bottom"]:
        _ = ax.spines[spine].set_visible(False)

    # hide tick labels
    _ = ax.set_xticks([])
    _ = ax.set_yticks([])

    _ = ax.set_title('Trip {}'.format(tid), fontweight="bold", fontfamily='serif', fontsize=16,
                     color='royalblue')

    plt.show()


def get_tracetime(line):
  start = line.find('--')+2
  end = line[start:].find('--')
  return datetime.strptime(line[start:end+start].strip().rstrip(), DATATIME_FORMAT)

def get_tid(line, pattern):
  start = line.find(pattern)+len(pattern)
  return line[start:start+36]

def get_deleted_trip_id(line):
  pass

args = setup_parser()
input_file = open(args.input, "r")

# {event_type: [{tracetime, metadata}]}
major_events = {}

# {cmd: [{pid, tid, cmd, stacktrace, timestamp, uptime, tracetime}]}
crashes = {}
current_crash = None
crash_skips = 0
backtrace_step = -1

# {id, plan, routes, created, response, navigated, better_proposals, deleted}
trip_data = {}
current_trip_id = None

for line in input_file:
  try:
    packet_id = float(line[0:line.find(" ")])
  except ValueError:
    continue

  if packet_id > args.end:
      break
  if packet_id < args.start:
      continue

  # Crash staff
  if current_crash != None:
    if CRASH_DEBUG in line:
      crash_skips = 0

      if backtrace_step != -1 and '#{:02d} pc'.format(backtrace_step) in line:
        current_crash['stacktrace'] = current_crash['stacktrace'] + line[line.find('#{:02d} pc'.format(backtrace_step)):]
        backtrace_step = backtrace_step+1
        continue

      if 'Cmdline' in line:
        current_crash['cmd'] = line[line.find('Cmdline: ')+9:].rstrip()
        continue

      if 'pid' in line:
        current_crash['pid'] = line[line.find('pid: ')+5:line.find('tid: ')]
        current_crash['tid'] = line[line.find('tid: ')+5:line.find(', name:')]
        continue

      if 'Timestamp:' in line:
        ts_str = line[line.find('Timestamp:')+11:].rstrip()
        current_crash['timestamp'] = datetime.strptime(ts_str[:25] + ts_str[29:], '%Y-%m-%d %H:%M:%S.%f%z')
        continue

      if 'Process uptime:' in line:
        continue

      if 'backtrace:' in line:
        backtrace_step = 0
        continue

    else:
      # It can happen that other process print inbetween crash process
      crash_skips = crash_skips + 1
      if crash_skips == 20:
        try:
          crashes[current_crash['cmd']].append(current_crash.copy())
        except KeyError:
          crashes[current_crash['cmd']] = [current_crash.copy()]
        current_crash = None
        backtrace_step = -1
        crash_skips = 0

  if CRASH_START in line:
    current_crash = EMPTY_CRASH
    current_crash['tracetime'] = get_tracetime(line)
    continue


  # Plan trip staff
  if PLAN_TRIP_REQUEST in line:
    tid = get_tid(line, PLAN_TRIP_REQUEST)
    assert tid not in trip_data
    new_trip = EMPTY_TRIP
    new_trip['id'] = tid
    new_trip['created'] = get_tracetime(line)
    new_trip['id'] = tid
    new_trip['plan'] = line[line.find('TripPlan'):]
    trip_data[tid] = new_trip.copy()

    continue

  if START_NAVIGATION_REQUEST in line:
    tid =  get_tid(line, START_NAVIGATION_REQUEST)
    assert tid in trip_data
    trip_data[tid]['navigated'] = get_tracetime(line)
    continue


  if DELETE_TRIP_RESPONSE in line:
    tid = get_tid(line, DELETE_TRIP_RESPONSE)
    assert tid in trip_data
    trip_data[tid]['deleted'] = get_tracetime(line)
    continue

  if CREATING_TRIP_SERVICE in line:
    ts = get_tracetime(line)
    try:
      major_events['create_trip_sevice'].append({'tracetime': ts, 'metadata': line})
    except KeyError as e:
      major_events['create_trip_sevice'] = [{'tracetime': ts, 'metadata': line}]

# Parsing is done, display timelines
print_crashes_report(crashes)
display_major_events(major_events, crashes)
display_plots(trip_data)
