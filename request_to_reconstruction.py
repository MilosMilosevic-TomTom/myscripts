#!python3

import argparse
import json
import subprocess
import polyline

style = '''
    <Style id="s0">
      <IconStyle>
        <color>FF0000FF</color>
        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon>
      </IconStyle>
      <LineStyle>
        <color>FF0000FF</color>
        <width>6</width>
      </LineStyle>
      <PolyStyle>
        <color>FF0000FF</color>
        <outline>0</outline>
      </PolyStyle>
    </Style>

    <Style id="s1">
      <IconStyle>
        <color>FF00CCFF</color>
        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon>
      </IconStyle>
      <LineStyle>
        <color>FF00CCFF</color>
        <width>6</width>
      </LineStyle>
      <PolyStyle>
        <color>FF00CCFF</color>
        <outline>0</outline>
      </PolyStyle>
    </Style>

    <Style id="s2">
      <IconStyle>
        <color>FF00FFFF</color>
        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon>
      </IconStyle>
      <LineStyle>
        <color>FF00FFFF</color>
        <width>6</width>
      </LineStyle>
      <PolyStyle>
        <color>FF00FFFF</color>
        <outline>0</outline>
      </PolyStyle>
    </Style>

    <Style id="s3">
      <IconStyle>
        <color>FF00FF00</color>
        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon>
      </IconStyle>
      <LineStyle>
        <color>FF00FF00</color>
        <width>6</width>
      </LineStyle>
      <PolyStyle>
        <color>FF00FF00</color>
        <outline>0</outline>
      </PolyStyle>
    </Style>

    <Style id="s4">
      <IconStyle>
        <color>FFFFFF00</color>
        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon>
      </IconStyle>
      <LineStyle>
        <color>FFFFFF00</color>
        <width>6</width>
      </LineStyle>
      <PolyStyle>
        <color>FFFFFF00</color>
        <outline>0</outline>
      </PolyStyle>
    </Style>

    <Style id="s5">
      <IconStyle>
        <color>FFFF0000</color>
        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon>
      </IconStyle>
      <LineStyle>
        <color>FFFF0000</color>
        <width>6</width>
      </LineStyle>
      <PolyStyle>
        <color>FFFF0000</color>
        <outline>0</outline>
      </PolyStyle>
    </Style>

    <Style id="s6">
      <IconStyle>
        <color>FFFF8080</color>
        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon>
      </IconStyle>
      <LineStyle>
        <color>FFFF8080</color>
        <width>6</width>
      </LineStyle>
      <PolyStyle>
        <color>FFFF8080</color>
        <outline>0</outline>
      </PolyStyle>
    </Style>

    <Style id="s7">
      <IconStyle>
        <color>FFFF00FF</color>
        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon>
      </IconStyle>
      <LineStyle>
        <color>FFFF00FF</color>
        <width>6</width>
      </LineStyle>
      <PolyStyle>
        <color>FFFF00FF</color>
        <outline>0</outline>
      </PolyStyle>
    </Style>

    <Style id="s8">
      <IconStyle>
        <color>FFFF6600</color>
        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon>
      </IconStyle>
      <LineStyle>
        <color>FFFF6600</color>
        <width>6</width>
      </LineStyle>
      <PolyStyle>
        <color>FFFF6600</color>
        <outline>0</outline>
      </PolyStyle>
    </Style>

    <Style id="s9">
      <IconStyle>
        <color>FF6633CC</color>
        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon>
      </IconStyle>
      <LineStyle>
        <color>FF6633CC</color>
        <width>6</width>
      </LineStyle>
      <PolyStyle>
        <color>FF6633CC</color>
        <outline>0</outline>
      </PolyStyle>
    </Style>

    <Style id="s10">
      <IconStyle>
        <color>FF2A2AA5</color>
        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon>
      </IconStyle>
      <LineStyle>
        <color>FF2A2AA5</color>
        <width>6</width>
      </LineStyle>
      <PolyStyle>
        <color>FF2A2AA5</color>
        <outline>0</outline>
      </PolyStyle>
    </Style>

    <Style id="s11">
      <IconStyle>
        <color>FF00008B</color>
        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon>
      </IconStyle>
      <LineStyle>
        <color>FF00008B</color>
        <width>6</width>
      </LineStyle>
      <PolyStyle>
        <color>FF00008B</color>
        <outline>0</outline>
      </PolyStyle>
    </Style>

    <Style id="s12">
      <IconStyle>
        <color>FFEBCE87</color>
        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon>
      </IconStyle>
      <LineStyle>
        <color>FFEBCE87</color>
        <width>6</width>
      </LineStyle>
      <PolyStyle>
        <color>FFEBCE87</color>
        <outline>0</outline>
      </PolyStyle>
    </Style>

    <Style id="s13">
      <IconStyle>
        <color>FF000000</color>
        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon>
      </IconStyle>
      <LineStyle>
        <color>FF000000</color>
        <width>6</width>
      </LineStyle>
      <PolyStyle>
        <color>FF000000</color>
        <outline>0</outline>
      </PolyStyle>
    </Style>
'''

def setup_parser():
    # Setup CLI arguments
    # autopep8: off
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', '-o', type=str, required=True, help="Output KML file name")
    parser.add_argument('--input', '-i', type=str, required=True, help="Data file with a polyline, post data or response")
    parser.add_argument('--leg', '-l', type=int, default=-1, help="By default take all the legs, number is zero-based")
    parser.add_argument('--route', '-r', type=int, default=0, help="In case there are multiple routes")
    parser.add_argument('--mode', '-m', type=str, default="post", help="Switch between post data and response data")
    parser.add_argument('--execute', '-e', type=str, help="Path to the routing-cli executable to execute polyline reconstruction job")
    parser.add_argument('--job', '-j', type=str, default='PolylineReconstruction', help="routing-cli job type")
    parser.add_argument('--map', type=str, help="Map to be used for polyline reconstruction job")
    parser.add_argument('--keystore', type=str, help="Keystore file to be used if polyline reconstruction job is used")
    parser.add_argument('--prefix', type=str, default='', help="Potential prefix for kml files")
    parser.add_argument('--truncate', type=int, default='0', help="Allows to truncate before execution for example for parital polyline resolving")
    parser.add_argument('--print', '-p', action='store_true', help="Print supporting points to std")
    args = parser.parse_args()

    if args.execute and (args.map is map or args.keystore is None):
        parser.error("Execute cannot be called without a map or without a keystore file")

    return args
    # autopep8: on

args = setup_parser()

document_start = '<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document><Folder><Folder>'
document_end = '</Folder></Folder></Document></kml>'

def add_pin(lon, lat, name=None):
    if name is not None:
        return "<Placemark><Point><coordinates>{},{}</coordinates></Point><name>{}</name></Placemark>".format(lon, lat, name)
    else:
        return "<Placemark><Point><coordinates>{},{}</coordinates></Point></Placemark>".format(lon, lat)

def add_leg(output_file, points, start, end, index):
    print("<Folder><name>leg_{}</name><Placemark><name>path</name><styleUrl>#s{}</styleUrl><LineString><coordinates>".format(index, index), file=output_file)
    for p in points[start:end]:
        print("{},{}".format(p["longitude"], p["latitude"]), file=output_file)
    print("</coordinates></LineString></Placemark></Folder>", file=output_file)

def encoded_to_supportingPoints(data):
    polyline_data = data["encodedPolyline"]
    polyline_precision = data["encodedPolylinePrecision"]
    decoded = polyline.decode(polyline_data, polyline_precision)
    converted_coordinates = [{"latitude": lat, "longitude": lon} for lat, lon in decoded]
    return converted_coordinates

with open(args.input) as json_file:
    data = json.load(json_file)
    output_file = open(args.output, "w+")

    leg_limits = [0]

    if args.mode == "response":
        points = []
        try:
            for leg in data["routes"][args.route]["legs"]:
                if "encodedPolyline" in leg:
                    leg["points"] = encoded_to_supportingPoints(leg)
                points.extend(leg["points"])
                leg_limits.append(leg_limits[-1] + len(leg["points"]))
        except KeyError as e:
            exit("Input file format wrong, key {} not found" + str(e))

        data["supportingPoints"] = points
    elif args.mode == "post":
        points = []
        if "legs" in data:
            for leg in data["legs"]:
                if "encodedPolyline" in leg:
                    leg["supportingPoints"] = encoded_to_supportingPoints(leg)
                points.extend(leg["supportingPoints"])
                leg_limits.append(leg_limits[-1] + len(leg["supportingPoints"]))
            data["supportingPoints"] = points
        else:
            if "encodedPolyline" in data:
                data["supportingPoints"] = encoded_to_supportingPoints(data)
            try:
                for w in data["pointWaypoints"]:
                    leg_limits.append(w["supportingPointIndex"])
            except KeyError as e:
                pass
            leg_limits.append(len(data["supportingPoints"])-1)
    else:
        exit("Unknown mode {}, supported modes are 'post' and 'response'".format(args.mode))

    print(leg_limits)
    if args.print:
        print(data["supportingPoints"])

    if args.truncate != 0:
        print("Truncated kml to {} points and dropped waypoints".format(args.truncate))
        data["supportingPoints"] = data["supportingPoints"][0:args.truncate]
        leg_limits = [0, args.truncate]

    if args.leg > len(leg_limits) - 2:
        exit("Input file contains {} legs while requested leg is {} (zero-based)".format(len(leg_limits)-1, args.leg))

    print(document_start, file=output_file)
    print(style, file=output_file)

    try:
        if args.leg == -1:
            for i in range(0, len(leg_limits)-1):
                add_leg(output_file, data["supportingPoints"], leg_limits[i], leg_limits[i+1], i)
        else:
            # One leg
            add_leg(output_file, data["supportingPoints"], leg_limits[args.leg], leg_limits[args.leg+1], args.leg)

    except KeyError as e:
        exit("Input file format wrong, key {} not found" + str(e))

    print(add_pin(data["supportingPoints"][0]["longitude"], data["supportingPoints"][0]["latitude"], "Start"), file=output_file)
    print(add_pin(data["supportingPoints"][-1]["longitude"], data["supportingPoints"][-1]["latitude"], "End"), file=output_file)
    for cnt, l in enumerate(leg_limits[1:-1]):
        print("Waypoint {}: {},{}".format(cnt+1, data["supportingPoints"][l]["latitude"], data["supportingPoints"][l]["longitude"]))
        print(add_pin(data["supportingPoints"][l]["longitude"], data["supportingPoints"][l]["latitude"], "Waypoint" + str(cnt+1)), file=output_file)

    print(document_end, file=output_file)

    output_file.close()

    if args.execute:
        cmd_args = [args.execute,
                    '--job-type', args.job,
                    '--map', args.map,
                    '--keystore', args.keystore,
                    '--output-dir', '/tmp/out',
                    '--save-search-space-kml', '--save-result-kml',
                    '--reference-route', args.output] + (['--output-name-prefix', args.prefix] if args.prefix != '' else [])

        if args.leg == -1:
            cmd_args += [
                '--origin', str(data["supportingPoints"][0]["latitude"]), str(data["supportingPoints"][0]["longitude"]),
                '--destination', str(data["supportingPoints"][-1]["latitude"]), str(data["supportingPoints"][-1]["longitude"])]
            if len(leg_limits) > 2:
                cmd_args += ['--waypoints']
                for l in leg_limits[1:-1]:
                    cmd_args += [str(data["supportingPoints"][l]["latitude"]), str(data["supportingPoints"][l]["longitude"])]
        else:
            cmd_args += [
                '--origin', str(data["supportingPoints"][leg_limits[args.leg]]["latitude"]), str(data["supportingPoints"][leg_limits[args.leg]]["longitude"]),
                '--destination', str(data["supportingPoints"][leg_limits[args.leg+1]-1]["latitude"]), str(data["supportingPoints"][leg_limits[args.leg+1]-1]["longitude"])]

        print("\n\n\n---------------\n\n\n" + " ".join(cmd_args) + "\n\n\n---------------\n\n\n")

        result = subprocess.run(cmd_args, capture_output=True, text=True)

        print(result.stdout)
        print(result.stderr)

