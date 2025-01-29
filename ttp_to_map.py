import folium
import sys

##########################################
# How to run
#
# python3 ttp_to_map.py <path_to_TTP_file>
#
# Requires: folium (install through pip)
#
# As a result you will get a 'car_path_map.html' file that can be opened in a browser
##########################################

# Function to read positions from the file
def read_positions(file_path):
    positions = []
    with open(file_path, 'r') as file:
        for line in file:
            # Skip metadata and empty lines
            if line.startswith('BEGIN') or line.startswith('#') or not line.strip():
                continue
            # Split the line and extract the latitude and longitude
            parts = line.split(',')
            if len(parts) >= 6:
                if int(parts[1]) != 245:
                    continue
                try:
                    latitude = float(parts[5])
                    longitude = float(parts[3])
                    positions.append((latitude, longitude))
                except ValueError:
                    continue
    return positions

# Function to create a map with the path
def create_map(positions):
    # Create a folium map centered at the average position
    if not positions:
        print("No positions available to plot.")
        return

    avg_lat = sum(lat for lat, _ in positions) / len(positions)
    avg_lon = sum(lon for _, lon in positions) / len(positions)
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=15)

    # Add lines between positions
    folium.PolyLine(positions, color='blue', weight=4, opacity=1).add_to(m)

    folium.Marker(location=positions[0]).add_to(m)
    folium.Marker(location=positions[-1]).add_to(m)

    # # Add markers for each position
    # for position in positions:
    #     folium.Marker(location=position).add_to(m)

    return m

# Main execution
positions = read_positions(sys.argv[1])
map_object = create_map(positions)

# Save the map to an HTML file
map_object.save('car_path_map.html')
