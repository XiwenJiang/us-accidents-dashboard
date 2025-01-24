import streamlit as st
import pandas as pd
import numpy as np
import pickle
from PIL import Image
import folium
from folium.plugins import MarkerCluster
import geopandas as gpd
from streamlit_folium import st_folium 

us_states = {'AK': 'Alaska',
 'AL': 'Alabama',
 'AR': 'Arkansas',
 'AS': 'American Samoa',
 'AZ': 'Arizona',
 'CA': 'California',
 'CO': 'Colorado',
 'CT': 'Connecticut',
 'DC': 'District of Columbia',
 'DE': 'Delaware',
 'FL': 'Florida',
 'GA': 'Georgia',
 'GU': 'Guam',
 'HI': 'Hawaii',
 'IA': 'Iowa',
 'ID': 'Idaho',
 'IL': 'Illinois',
 'IN': 'Indiana',
 'KS': 'Kansas',
 'KY': 'Kentucky',
 'LA': 'Louisiana',
 'MA': 'Massachusetts',
 'MD': 'Maryland',
 'ME': 'Maine',
 'MI': 'Michigan',
 'MN': 'Minnesota',
 'MO': 'Missouri',
 'MP': 'Northern Mariana Islands',
 'MS': 'Mississippi',
 'MT': 'Montana',
 'NC': 'North Carolina',
 'ND': 'North Dakota',
 'NE': 'Nebraska',
 'NH': 'New Hampshire',
 'NJ': 'New Jersey',
 'NM': 'New Mexico',
 'NV': 'Nevada',
 'NY': 'New York',
 'OH': 'Ohio',
 'OK': 'Oklahoma',
 'OR': 'Oregon',
 'PA': 'Pennsylvania',
 'PR': 'Puerto Rico',
 'RI': 'Rhode Island',
 'SC': 'South Carolina',
 'SD': 'South Dakota',
 'TN': 'Tennessee',
 'TX': 'Texas',
 'UT': 'Utah',
 'VA': 'Virginia',
 'VI': 'Virgin Islands',
 'VT': 'Vermont',
 'WA': 'Washington',
 'WI': 'Wisconsin',
 'WV': 'West Virginia',
 'WY': 'Wyoming'}
def state_code(state_code): return us_states[state_code]

st.write("""
         # US Traffic Accidents Data | 2016 - 2023
         The primary objectives of this analysis are to:
            - **Visualize Geographic Data**: Leverage geospatial data to create intuitive and informative visualizations.
            - **Identify Accident Hotspots**: Locate and analyze regions with high frequencies of traffic accidents.
         """)

# Load dataset
@st.cache_data
def load_data():
    data = pd.read_csv('temp/US_Accidents_March23_sampled_500k.csv')
    # Select columns for analysis
    basic_columns = ['ID', 'Severity', 
                    'Start_Time', 'End_Time', 
                    'Start_Lat', 'Start_Lng', 
                    'Distance(mi)', 'Sunrise_Sunset']
    geo_columns = ['Street','City', 'County', 'State', 'Zipcode', 'Country', 'Timezone']
    road_conditions = ['Bump', 'Crossing', 'Give_Way', 'Junction', 'Stop', 'No_Exit', 'Traffic_Signal', 'Turning_Loop']
    weather_columns = ['Temperature(F)', 'Humidity(%)', 'Pressure(in)', 'Visibility(mi)', 'Wind_Direction', 'Wind_Speed(mph)', 'Precipitation(in)', 'Weather_Condition']
    description_columns = ['Description']
    all_columns = basic_columns + geo_columns + road_conditions + weather_columns + description_columns
    data = data[all_columns]

    # Preprocess data
    # Intergrate datetime columns
    data['Start_Time'] = pd.to_datetime(data['Start_Time'].str.replace(r'\.\d+$', '', regex=True))
    data['End_Time'] = pd.to_datetime(data['End_Time'].str.replace(r'\.\d+$', '', regex=True))

    # Severity Levels
    severity_level = {1: 'Low', 2: 'Medium', 3: 'High', 4: 'Critical'}
    data['Severity'] = data['Severity'].map(severity_level)

    # State Code
    data['State_Code'] = data['State']
    data['State'] = data['State_Code'].apply(state_code)

    return data

data = load_data()


# Sidebar for user input controls

st.sidebar.title("Select Filters")
years = data['Start_Time'].dt.year.unique().tolist()
years.sort()
years.insert(0, 'All Years')
selected_years = st.sidebar.multiselect(
    "Select Year", years, default=years[0]  # Default to all years
)

# Filter data based on selected years
if 'All Years' in selected_years:
    filtered_data = data  # Include all data if 'All Years' is selected
else:
    filtered_data = data[data['Start_Time'].dt.year.isin(selected_years)]


month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

month = month_order.copy()
month.insert(0, 'All Months')
selected_month = st.sidebar.multiselect(
    "Select Month", month, default=month[0]  # Default to all months
)
if 'All Months' in selected_month:
    filtered_data = filtered_data  # Include all data if 'All Months' is selected
else:
    filtered_data = filtered_data[filtered_data['Start_Time'].dt.month_name().isin(selected_month)]

time_of_day = st.sidebar.radio("Select Time of Day", ['Day', 'Night'])

if time_of_day == 'Day':
    filtered_data = filtered_data[filtered_data['Sunrise_Sunset'] == 'Day']
else:
    filtered_data = filtered_data[filtered_data['Sunrise_Sunset'] == 'Night']

# Display filtered data
st.write(f"Showing accidents for {', '.join([str(year) for year in selected_years])} {month} during {time_of_day} time.")
st.write(filtered_data.head())






# Initialize the map

def create_map(df_loc, latitude, longitude, zoom, tiles='OpenStreetMap'):
    """
    Generate a Folium Map with clustered markers of accident locations.
    """
    world_map = folium.Map(location=[latitude, longitude], zoom_start=zoom, tiles=tiles)
    marker_cluster = MarkerCluster().add_to(world_map)

    # Iterate over the DataFrame rows and add each marker to the cluster
    for idx, row in df_loc.iterrows():
        folium.Marker(
            location=[row['Start_Lat'], row['Start_Lng']],
            # You can add more attributes to your marker here, such as a popup
            popup=f"Lat, Lng: {row['Start_Lat']}, {row['Start_Lng']}"
        ).add_to(marker_cluster)

    return world_map

map_us = create_map(filtered_data, 39.50, -98.35, 4)

# Display the map in Streamlit using st_folium
st.write("### Accident Locations on the Map")
st_folium(map_us, width=725, height=500)  # Display the map with specific width and height




# Fix SettingWithCopyWarning
filtered_data.loc[:, 'Start_Time'] = filtered_data['Start_Time'].astype(str)
filtered_data.loc[:, 'End_Time'] = filtered_data['End_Time'].astype(str)

# # Function to create a Folium map with clustered markers
# def create_map(df_loc, latitude, longitude, zoom, tiles='OpenStreetMap'):
#     """
#     Generate a Folium Map with clustered markers of accident locations.
#     """
#     world_map = folium.Map(location=[latitude, longitude], zoom_start=zoom, tiles=tiles)
#     marker_cluster = MarkerCluster().add_to(world_map)

#     # Iterate over the DataFrame rows and add each marker to the cluster
#     for idx, row in df_loc.iterrows():
#         folium.Marker(
#             location=[row['Start_Lat'], row['Start_Lng']],
#             # Popup with accident details (customize as needed)
#             popup=f"Lat, Lng: {row['Start_Lat']}, {row['Start_Lng']}<br>Severity: {row['Severity']}<br>City: {row['City']}"
#         ).add_to(marker_cluster)

#     return world_map

# # Create the map centered on the US
# map_us = create_map(filtered_data, 39.50, -98.35, 4)

# # Display the map in Streamlit using st_folium
# st.write("### Accident Locations on the Map")
# st_folium(map_us, width=725, height=500)  # Display the map with specific width and height

# Convert DataFrame to GeoDataFrame for efficient handling of geospatial data
gdf = gpd.GeoDataFrame(filtered_data, geometry=gpd.points_from_xy(filtered_data['Start_Lng'], filtered_data['Start_Lat']))

# Convert GeoDataFrame to GeoJSON format
geojson_data = gdf.to_json()

# Initialize the Folium map centered around the US
m = folium.Map(location=[39.50, -98.35], zoom_start=4)

# Add the GeoJSON data to the map as a single object
folium.GeoJson(
    geojson_data, 
    popup=folium.GeoJsonPopup(fields=["Severity", "City", "State", "Start_Time", "Distance(mi)"], 
                              labels=True, localize=True)
).add_to(m)

# Display the map in Streamlit using st_folium
st.write("### Accident Locations on the Map")
st_folium(m, width=725, height=500)  # Display the map with specific width and height




