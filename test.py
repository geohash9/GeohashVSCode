import geohash2
import folium
import geopandas as gpd
from shapely.geometry import Polygon, Point
from folium.plugins import MeasureControl, Fullscreen
import random
from IPython.display import display

# Load GeoJSON files for campus boundaries and different areas
CAMPUS_AREA_CATEGORY_LAYER = 'CAMPUS_AREA_CATEGORY_LAYER.geojson'
BUILDING_CODES_LAYER = 'BUILDING_CODES_LAYER.geojson'
IIT_KGP_NEW_BOUNDARY = 'IIT_KGP_NEW_BOUNDARY.geojson'

IIT_KGP_NEW_BOUNDARY_gdf = gpd.read_file(IIT_KGP_NEW_BOUNDARY)
BUILDING_CODES_gdf = gpd.read_file(BUILDING_CODES_LAYER)
CAMPUS_AREA_CATEGORY_gdf = gpd.read_file(CAMPUS_AREA_CATEGORY_LAYER)

# Extract the campus boundary polygon from the GeoDataFrame
campus_polygon = IIT_KGP_NEW_BOUNDARY_gdf.geometry.iloc[0]

# Calculate the centroid of the campus polygon
centroid = campus_polygon.centroid
location = [campus_polygon.centroid.y, campus_polygon.centroid.x]

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

for i in range(grid_size):
    for j in range(grid_size):
        latitude = bounds[1] + i * step_lat
        longitude = bounds[0] + j * step_lon
        point = Point(longitude, latitude)

        # Check if the generated point is within the campus polygon
        if campus_polygon.contains(point):
            # Fetch campus area category from CAMPUS_AREA_CATEGORY_gdf
            category_df = CAMPUS_AREA_CATEGORY_gdf.geometry.contains(point).any()
            campus_area_category = category_df.iloc[0]['Category']
            print("campus_area_category", campus_area_category)
            if not category_df.empty:
                campus_area_category = category_df.iloc[0]['Category']
            else:
#                 print(f"Warning: No matching category found for point {point}")
                continue

            # Fetch building code from BUILDING_CODES_gdf
            code_df = BUILDING_CODES_gdf[BUILDING_CODES_gdf.geometry.contains(point)]
            if not code_df.empty:
                # Add print statements to debug the issue
                print(f"code_df length: {len(code_df)}")
                print(f"code_df: {code_df}")

                building_code = code_df.iloc[0]['Code']
            else:
#                 print(f"Warning: No matching building code found for point {point}")
                continue

            # Generate a random two-digit number
            random_number = str(random.randint(10, 99))

            # Create a custom geohash code with campus area category, building code, 'G', and random number
            custom_geohash = campus_area_category + building_code + 'G' + random_number

            geohash_codes.append(custom_geohash)

            # Define coordinates for the corners of the geohash cell
            corners = [
                (latitude, longitude),
                (latitude + step_lat, longitude),
                (latitude + step_lat, longitude + step_lon),
                (latitude, longitude + step_lon),
            ]

            # Create a popup with the custom geohash code
            popup_text = f'Custom Geohash: {custom_geohash}'
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

folium.Marker(location, tooltip="Centroid: " + geohashcode11).add_to(campus_map)
# Display the map with Esri satellite imagery as the basemap, custom geohash grids, and the measurement tool
display(campus_map)

# The generated custom geohash codes are stored in the geohash_codes list
# print(geohash_codes)

output_html_file = "campus_map.html"
campus_map.save(output_html_file)
