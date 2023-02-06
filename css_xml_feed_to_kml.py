#!/usr/bin/python3
import argparse
import json
import math
import sys
import xml.etree.ElementTree as ET
import xmltodict

from xml.dom import minidom
from xml.sax.saxutils import unescape

# Definition of xml tags
NAMESPACE = "{http://www.tomtom.com/service/tis/chargingstation/static/1.9}"
PRIMITIVES = "{http://www.tomtom.com/service/tis/primitives/1.6}"
GEOMETRIES = "{http://www.tomtom.com/service/tis/location/geometries/1.6}"

ACCESS_RESTRICTED_TAG = NAMESPACE+'accessibilityType'
BRANDS_TAG = NAMESPACE+'brands'
CATEGORY_ID_TAG = NAMESPACE+'categoryId'
CHARGING_PARK_TAG = NAMESPACE+'chargingPark'
CHARGING_POINTS_TAG = NAMESPACE+'chargingPoints'
CHARGING_POINT_TAG = NAMESPACE+'chargingPoint'
CHARGING_STATION_TAG = NAMESPACE+'chargingStation'
CHARGING_STATIONS_TAG = NAMESPACE+'chargingStations'
CONNECTOR_TAG = NAMESPACE+'connector'
CONNECTORS_TAG = NAMESPACE+'connectors'
CURRENT_TAG = NAMESPACE+'current'
CURRENT_TYPE_TAG = NAMESPACE+'currentType'
ENTRY_LOCATION_TAG = GEOMETRIES+'entryLocation'
LOCATIONS_TAG = NAMESPACE+'locations'
LONGITUDE_TAG = PRIMITIVES+'longitude'
LATITUDE_TAG = PRIMITIVES+'latitude'
METHOD_TAG = NAMESPACE+'method'
NAME_TAG = NAMESPACE+'name'
PAYMENT_OPTIONS_TAG = NAMESPACE+'paymentOptions'
PAYMENT_OPTION_TAG = NAMESPACE+'paymentOption'
POINT_LOCATION_TAG = GEOMETRIES+'pointLocation'
PLUG_TYPE_TAG = NAMESPACE+'plugType'
PROPERTIES_TAG = NAMESPACE+'properties'
RATED_POWER_TAG = NAMESPACE+'ratedPower'
UUID_TAG = NAMESPACE+'uuid'
VOLTAGE_TAG = NAMESPACE+'voltage'

DEFAULT_PROXIMITY = [.0,.0,.0]

def setup_parser():
  # Setup CLI arguments
  parser = argparse.ArgumentParser()
  parser.add_argument("--feed_xml_file", required=True, type=str,
    help="Path to a xml file contatining charging station feed")
  parser.add_argument("--brands", nargs="*", type=str, default=[],
    help="List of brands, case sensitive, space has to be escaped with '\ '")
  parser.add_argument("--plug_types", nargs="*", type=str, default=[],
    help="List of compatible plug types")
  parser.add_argument("--proximity", nargs=3, type=float, default=DEFAULT_PROXIMITY,
    help="Area of the charging stations in format: latitude longitude diameter_in_km")
  parser.add_argument("--uuids", nargs="*", type=str, default=[],
    help="Exctract only given uuids")
  parser.add_argument("--exclude_restricted", action='store_true',
    help="Filter out restircted charging stations")
  parser.add_argument("--category_ids_analytics", nargs="*", type=str, default=None,
    help="List of category ids to count, none means count any")
  parser.add_argument("--points_distance", type=float, default=.0,
    help="Minimal distance between navigable coordinate and POI coordinate")
  parser.add_argument("--min_power", type=float, default=.0,
    help="Minimal power for a charing station to be considered")

  return parser.parse_args()

def filter_by_brands(charging_park, desired_brands):
  # Returns a set of brands which are compatible with given charging station
  # Also returns a set of all brands that are supported by the given charging station
  all_brands = set()
  compatible_brands = set()
  properties = charging_park.find(PROPERTIES_TAG)
  for p in properties:
    if p.tag == PAYMENT_OPTIONS_TAG:
      for payment_option in p.findall(PAYMENT_OPTION_TAG):
        if payment_option.find(METHOD_TAG).text == "Subscription" and payment_option.find(BRANDS_TAG):
          brands = [b.text for b in payment_option.find(BRANDS_TAG)]
          all_brands.update(brands)
          for desired_brand in desired_brands:
            if desired_brand in brands:
              compatible_brands.add(desired_brand)
  return compatible_brands, all_brands

def get_all_connectors(charging_park, exclude_restricted):
  # Return all connectors within the charging park
  all_connectors = []
  charging_stations = charging_park.find(CHARGING_STATIONS_TAG).findall(CHARGING_STATION_TAG)
  for charging_station in charging_stations:
    if exclude_restricted and charging_station.find(ACCESS_RESTRICTED_TAG) != None \
    and charging_station.find(ACCESS_RESTRICTED_TAG).text == "Restricted":
      continue
    charging_points = charging_station.find(CHARGING_POINTS_TAG).findall(CHARGING_POINT_TAG)
    for charging_point in charging_points:
      all_connectors += charging_point.find(CONNECTORS_TAG).findall(CONNECTOR_TAG)
  return all_connectors

def filter_by_plug_types(charging_park, desired_plug_types, exclude_restricted):
  # Return a list of connectors which are compatible with given plug types
  compatible_connectors = []
  for connector in get_all_connectors(charging_park, exclude_restricted):
    if connector.find(PLUG_TYPE_TAG).text in desired_plug_types:
      compatible_connectors.append(connector)
  return compatible_connectors

def generate_description_for_connector(connector):
  plug_type = connector.find(PLUG_TYPE_TAG)
  rated_power = connector.find(RATED_POWER_TAG)
  voltage = connector.find(VOLTAGE_TAG)
  current = connector.find(CURRENT_TAG)
  current_type = connector.find(CURRENT_TYPE_TAG)

  description = "\n"
  description += "Plug Type: " + plug_type.text + "\n"
  description += "Rated power: " + (rated_power.text if rated_power is not None else "") + "\n"
  description += "Voltage: " + (voltage.text if voltage is not None else "") + "\n"
  description += "Current: " + (current.text if current is not None else "") + "\n"
  description += "Current type:" + (current_type.text if current_type is not None else "") + "\n"

  return description

def generate_description_for_charging_park(charging_park, compatible_connectors):
  description = "Charging park: " + charging_park.find(UUID_TAG).text + "\n"
  description = description + "Name: " + charging_park.find(PROPERTIES_TAG).find(NAME_TAG).text + "\n"
  charging_stations = charging_park.find(CHARGING_STATIONS_TAG).findall(CHARGING_STATION_TAG)
  for charging_station in charging_stations:
    description += "\n----\nCharging station: " + charging_station.find(UUID_TAG).text + "\n"
    if charging_station.find(ACCESS_RESTRICTED_TAG) != None and charging_station.find(ACCESS_RESTRICTED_TAG).text == "Restricted":
      description += "RESTRICTED\n"
    charging_points = charging_station.find(CHARGING_POINTS_TAG).findall(CHARGING_POINT_TAG)
    for charging_point in charging_points:
      description += "Charging point: " + charging_point.find(UUID_TAG).text
      for connector in charging_point.find(CONNECTORS_TAG).findall(CONNECTOR_TAG):
        if connector in compatible_connectors:
          description += " COMPATIBLE"
        description += generate_description_for_connector(connector) + "\n"
  return description

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

def in_within_proximity(latitude, longitude, desired_proximity):
  dist = calculate_distance(latitude, longitude, desired_proximity[0], desired_proximity[1])
  return dist < desired_proximity[2]

#################### Main ####################

args = setup_parser()

input_file_name = args.feed_xml_file
input_file = open(input_file_name, "r")
output_file_name = input_file_name.replace(".xml", ".kml")

desired_brands = args.brands
desired_plug_types = args.plug_types
desired_proximity = args.proximity
desired_uuids = args.uuids
exclude_restricted = args.exclude_restricted
desired_category_ids = args.category_ids_analytics
different_brands = set()
different_category_ids = set()
points_distance = args.points_distance
min_power = args.min_power

feed = ET.parse(input_file_name).getroot()

##### Filter charging stations #####

filtered_charging_parks = []
category_ids_found = 0
category_ids_missed = 0
category_ids_blank = 0

for charging_park in feed.findall(CHARGING_PARK_TAG):
  # List of charging brands compatible with preferred brand
  brands_desc = ""
  # Description including list of all compatible charging points
  description = ""
  # Exctracted coordinates
  coordinates = ""
  # Max power among all compatible charging points
  max_power = .0

  # General info about the charging park
  location = charging_park.find(LOCATIONS_TAG).find(POINT_LOCATION_TAG)
  latitude = float(location.find(LATITUDE_TAG).text)
  longitude = float(location.find(LONGITUDE_TAG).text)
  coordinates = "{0},{1},0".format(longitude, latitude)

  # Filter based on the uuids
  if desired_uuids:
    if charging_park.find(UUID_TAG).text not in desired_uuids:
      continue

  # If desired brands are specified filter based on them
  if desired_brands:
    compatible_brands, all_brands = filter_by_brands(charging_park, desired_brands)
    different_brands.update(all_brands)
    if not compatible_brands:
      continue
    brands_desc = str(list(compatible_brands))

  # If desired proximity is set, filter based on it
  if desired_proximity != DEFAULT_PROXIMITY:
    if not in_within_proximity(latitude, longitude, desired_proximity):
      continue

  # If desired plug_types are specified fileter based on them
  compatible_connectors = []
  if desired_plug_types:
    compatible_connectors = filter_by_plug_types(charging_park, desired_plug_types, exclude_restricted)
    if not compatible_connectors:
      continue
  else:
    compatible_connectors = get_all_connectors(charging_park, exclude_restricted)

  # If the distance between entry point location and POI location is smaller than desired, skip the charging park
  if points_distance != .0:
    if charging_park.find(LOCATIONS_TAG).find(ENTRY_LOCATION_TAG) == None:
      continue
    entry_location = charging_park.find(LOCATIONS_TAG).find(ENTRY_LOCATION_TAG)
    entry_latitude = float(entry_location.find(LATITUDE_TAG).text)
    entry_longitude = float(entry_location.find(LONGITUDE_TAG).text)
    entry_coordinates = "{0},{1},0".format(entry_longitude, entry_latitude)

    dist = calculate_distance(latitude, longitude, entry_latitude, entry_longitude)

    if dist < points_distance:
      continue
    ET.SubElement(charging_park, "entry").text = entry_coordinates

  # If there is no compatible connector, skip the charging park
  if len(compatible_connectors) == 0:
    continue

  # Calculate max power
  for connector in compatible_connectors:
    rated_power = connector.find(RATED_POWER_TAG)
    if rated_power is not None and float(rated_power.text) > max_power:
      max_power = float(rated_power.text)

  # Filter out chargers which are "weaker" than min_power
  if max_power < min_power:
    continue

  # Generate description
  description = generate_description_for_charging_park(charging_park, compatible_connectors)

  if desired_category_ids != None:
    category_id = charging_park.find(CATEGORY_ID_TAG)
    if category_id != None:
      if category_id.text not in different_category_ids:
        different_category_ids.add(category_id.text)
      if category_id.text in desired_category_ids:
        category_ids_found += 1
      else:
        category_ids_missed += 1
    else:
      category_ids_blank += 1

  # Save the data for later
  ET.SubElement(charging_park, "description").text = description
  ET.SubElement(charging_park, "brands_desc").text = brands_desc
  ET.SubElement(charging_park, "maxPower").text = str(max_power)
  ET.SubElement(charging_park, "compatible_connectors").text = len(compatible_connectors)
  ET.SubElement(charging_park, "coordinates").text = coordinates
  filtered_charging_parks.append(charging_park)

print("Extracted " + str(len(filtered_charging_parks)) + " charging parks")
if len(different_brands) != 0:
  print("Different brands are:")
  print(different_brands)
if desired_category_ids != None:
  print("Category id analysis:")
  print("Desired ids: " + str(desired_category_ids))
  print("found: {0}, missed: {1}, blank: {2}".format(category_ids_found, category_ids_missed, category_ids_blank))
  print("unique are: " + str(different_category_ids))

##### Generate kml file #####

kml = ET.Element("kml", xmlns="http://www.opengis.net/kml/2.2")
document = ET.SubElement(kml, "Document")
ET.SubElement(document, "name").text = output_file_name
ET.SubElement(document, "visibility").text = "1"
ET.SubElement(document, "open").text = "1"

if desired_proximity != DEFAULT_PROXIMITY:
  # Add style for proximity center
  style = ET.SubElement(document, "Style", id="ProximityCenter")
  icon_style = ET.SubElement(style, "IconStyle")
  ET.SubElement(icon_style, "scale").text = "2"
  icon = ET.SubElement(icon_style, "Icon")
  ET.SubElement(icon, "href").text = "http://maps.google.com/mapfiles/kml/paddle/red-circle.png"

  # Add placemark for proximity center
  placemark = ET.SubElement(document, "Placemark")
  point = ET.SubElement(placemark, "Point")
  ET.SubElement(placemark, "styleUrl").text = "#ProximityCenter"
  ET.SubElement(point, "coordinates").text = "{0}, {1}, 0".format(desired_proximity[1], desired_proximity[0])
  ET.SubElement(placemark, "name").text = "Proximity center"


for filtered_charging_park in filtered_charging_parks:
  placemark = ET.SubElement(document, "Placemark")
  point = ET.SubElement(placemark, "Point")
  ET.SubElement(point, "coordinates").text = filtered_charging_park.find('coordinates').text
  # Extract description
  name = "{0} ({1}) {2}".format(filtered_charging_park.find("maxPower").text,
                                filtered_charging_park.find("compatible_connectors").text,
                                filtered_charging_park.find('brands_desc').text)
  ET.SubElement(placemark, "description").text = filtered_charging_park.find('description').text
  ET.SubElement(placemark, "name").text = name

  if points_distance != .0:
    placemark = ET.SubElement(document, "Placemark")
    point = ET.SubElement(placemark, "Point")
    ET.SubElement(point, "coordinates").text = filtered_charging_park.find('entry').text
    ET.SubElement(placemark, "name").text = "entry"


tree = ET.ElementTree(kml)
xmlstr = minidom.parseString(ET.tostring(kml)).toprettyxml(indent="  ")
with open(output_file_name, "w") as f:
    f.write(xmlstr)