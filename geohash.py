import geohash2
import folium
import geopandas as gpd
from shapely.geometry import Polygon, Point
from folium.plugins import MeasureControl, Fullscreen
import random
from IPython.display import display

# Load GeoJSON files for campus boundaries and different areas
campus_boundary_geojson = 'IITKGP_CAMPUS_BOUNDARY.geojson'
academic_area_geojson = 'Academic_Area.geojson'
hostel_area_geojson = 'Hostel_Area.geojson'
open_spaces_geojson = 'Open_Spaces.geojson'
residential_area_geojson = 'Residential_Area.geojson'

campus_boundary_gdf = gpd.read_file(campus_boundary_geojson)
academic_area_gdf = gpd.read_file(academic_area_geojson)
hostel_area_gdf = gpd.read_file(hostel_area_geojson)
open_spaces_gdf = gpd.read_file(open_spaces_geojson)
residential_area_gdf = gpd.read_file(residential_area_geojson)

# Extract the campus boundary polygon from the GeoDataFrame
campus_polygon = campus_boundary_gdf.geometry.iloc[0]

# Calculate the centroid of the campus polygon
centroid = campus_polygon.centroid

location=[campus_polygon.centroid.y, campus_polygon.centroid.x]

# Create a folium map centered around the campus
campus_map = folium.Map(
    location=[centroid.y, centroid.x],
    zoom_start=15,
    height=600
)

# Add Esri satellite imagery as the basemap
esri_satellite_url = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
folium.TileLayer(
    tiles=esri_satellite_url,
    attr='Esri',
    name='Esri Satellite',
    overlay=False,
).add_to(campus_map)

# Generate and display geohash grids inside the campus polygon for precision level 8
grid_size = 145  # Number of points in each direction
bounds = campus_polygon.bounds  # Get the bounding box of the campus polygon

# Create a list to store geohash codes for precision level 8
geohash_codes = []

step_lat = (bounds[3] - bounds[1]) / grid_size
step_lon = (bounds[2] - bounds[0]) / grid_size

# Define custom geohash characters for different areas
area_characters = {
    "Academic": "A",
    "Hostel": "H",
    "Open Spaces": "O",
    "Residential": "R",
}

for i in range(grid_size):
    for j in range(grid_size):
        latitude = bounds[1] + i * step_lat
        longitude = bounds[0] + j * step_lon
        point = Point(longitude, latitude)

        # Check if the generated point is within the campus polygon
        if campus_polygon.contains(point):
            # Determine the direction relative to the centroid
            direction = ""
            if latitude >= centroid.y and longitude >= centroid.x:
                direction = "NE"
            elif latitude >= centroid.y and longitude < centroid.x:
                direction = "NW"
            elif latitude < centroid.y and longitude >= centroid.x:
                direction = "SE"
            elif latitude < centroid.y and longitude < centroid.x:
                direction = "SW"

            # Determine the area type based on which polygon the point is in
            area_type = None
            if academic_area_gdf.geometry.contains(point).any():
                area_type = "Academic"
            elif hostel_area_gdf.geometry.contains(point).any():
                area_type = "Hostel"
            elif open_spaces_gdf.geometry.contains(point).any():
                area_type = "Open Spaces"
            elif residential_area_gdf.geometry.contains(point).any():
                area_type = "Residential"

            # Generate a random three-digit number
            random_number = str(random.randint(100, 999))

            # Encode the point's coordinates using precision 8
            original_geohash = geohash2.encode(latitude, longitude, precision=8)

            # Create a custom geohash code with direction, area character, and random number
            custom_geohash = direction + area_characters.get(area_type, "X") + random_number

            geohash_codes.append(custom_geohash)

            # Define coordinates for the corners of the geohash cell
            corners = [
                (latitude, longitude),
                (latitude + step_lat, longitude),
                (latitude + step_lat, longitude + step_lon),
                (latitude, longitude + step_lon),
            ]

            # Create a popup with both original and custom geohash codes
            popup_text = f'Original Geohash: {original_geohash}<br>Custom Geohash: {custom_geohash}'
            popup = folium.Popup(popup_text, max_width=400)

            # Create a polygon using the coordinates
            folium.Polygon(
                locations=corners,
                popup=popup,
                color='red',
                fill=True,
                fill_color='#000000',
                fill_opacity=0.3,
                weight=0.5,
            ).add_to(campus_map)

# Add the MeasureControl to the map
campus_map.add_child(MeasureControl(primary_length_unit='meters', primary_area_unit='sqmeters'))

Fullscreen().add_to(campus_map)
geohashcode11 = geohash2.encode(location[0], location[1], precision=8)

folium.Marker(location, tooltip="Centroid: "+ geohashcode11).add_to(campus_map)
# Display the map with Esri satellite imagery as the basemap, custom geohash grids, and the measurement tool
display(campus_map)

# The generated custom geohash codes are stored in the geohash_codes list
# print(geohash_codes)

output_html_file = "campus_map.html"
campus_map.save(output_html_file)
