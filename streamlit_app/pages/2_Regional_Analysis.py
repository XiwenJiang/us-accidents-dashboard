import streamlit as st
import pandas as pd
import plotly.express as px
import folium
import requests
from folium.features import GeoJsonTooltip

from streamlit_folium import st_folium

us_cities_coords = {
    "Miami": {"lat": 25.7617, "lon": -80.1918},
    "Houston": {"lat": 29.7604, "lon": -95.3698},
    "Los Angeles": {"lat": 34.0522, "lon": -118.2437},
    "Charlotte": {"lat": 35.2271, "lon": -80.8431},
    "Dallas": {"lat": 32.7767, "lon": -96.7970},
    "Orlando": {"lat": 28.5383, "lon": -81.3792},
    "Austin": {"lat": 30.2672, "lon": -97.7431},
    "Raleigh": {"lat": 35.7796, "lon": -78.6382},
    "Nashville": {"lat": 36.1627, "lon": -86.7816},
    "Baton Rouge": {"lat": 30.4515, "lon": -91.1871},
    "Atlanta": {"lat": 33.7490, "lon": -84.3880},
    "Sacramento": {"lat": 38.5816, "lon": -121.4944},
    "San Diego": {"lat": 32.7157, "lon": -117.1611},
    "Phoenix": {"lat": 33.4484, "lon": -112.0740},
    "Minneapolis": {"lat": 44.9778, "lon": -93.2650},
    "Richmond": {"lat": 37.5407, "lon": -77.4360},
    "Oklahoma City": {"lat": 35.4676, "lon": -97.5164},
    "Jacksonville": {"lat": 30.3322, "lon": -81.6557},
    "Tucson": {"lat": 32.2226, "lon": -110.9747},
    "Columbia": {"lat": 34.0007, "lon": -81.0348},
    "Greenville": {"lat": 34.8526, "lon": -82.3940},
    "San Antonio": {"lat": 29.4241, "lon": -98.4936},
    "Saint Paul": {"lat": 44.9537, "lon": -93.0900},
    "Seattle": {"lat": 47.6062, "lon": -122.3321},
    "Portland": {"lat": 45.5051, "lon": -122.6750},
    "San Jose": {"lat": 37.3382, "lon": -121.8863},
    "Indianapolis": {"lat": 39.7684, "lon": -86.1581},
    "Denver": {"lat": 39.7392, "lon": -104.9903},
    "Chicago": {"lat": 41.8781, "lon": -87.6298},
    "Tampa": {"lat": 27.9506, "lon": -82.4572},
    "Kansas City": {"lat": 39.0997, "lon": -94.5786},
    "Tulsa": {"lat": 36.1540, "lon": -95.9928},
    "Bronx": {"lat": 40.8448, "lon": -73.8648},
    "New Orleans": {"lat": 29.9511, "lon": -90.0715},
    "Rochester": {"lat": 43.1566, "lon": -77.6088},
    "Riverside": {"lat": 33.9806, "lon": -117.3755},
    "Fort Lauderdale": {"lat": 26.1224, "lon": -80.1373},
    "Detroit": {"lat": 42.3314, "lon": -83.0458},
    "Grand Rapids": {"lat": 42.9634, "lon": -85.6681},
    "Dayton": {"lat": 39.7589, "lon": -84.1916},
    "Oakland": {"lat": 37.8044, "lon": -122.2712},
    "Columbus": {"lat": 39.9612, "lon": -82.9988},
    "Bakersfield": {"lat": 35.3733, "lon": -119.0187},
    "New York": {"lat": 40.7128, "lon": -74.0060},
    "Brooklyn": {"lat": 40.6782, "lon": -73.9442},
    "San Bernardino": {"lat": 34.1083, "lon": -117.2898},
    "Omaha": {"lat": 41.2565, "lon": -95.9345},
    "Corona": {"lat": 33.8753, "lon": -117.5664},
    "Anaheim": {"lat": 33.8366, "lon": -117.9143},
    "Long Beach": {"lat": 33.7701, "lon": -118.1937}
}


st.title("State Analysis")
st.write("Explore accident data by state.")
st.write("This page will include state-specific statistics and visualizations.")

data = st.session_state.data

st.sidebar.title("Select Filters")
years = data['Year'].unique().tolist()
years.sort()
years.insert(0, '2016-2023')
selected_years = st.sidebar.multiselect(
    "Select Year", years, default=years[0]  # Default to all years
)

if '2016-2023' not in selected_years:
    filtered_data = data[data['Year'].isin(selected_years)]
else:
    filtered_data = data


col1, col2 = st.columns([1,1])

# Aggregate accident counts by State and Severity
state_severity_counts = filtered_data.groupby(['State', 'Severity']).agg({'ID': 'count'}).reset_index()
state_severity_counts.columns = ['State', 'Severity', 'Accident_Count']

# Compute total counts for each state and percentages
state_total_counts = filtered_data.groupby('State').agg({'ID': 'count'}).reset_index()
state_total_counts.columns = ['State', 'Total_Accidents']

# Merge total counts back to the severity-level data
state_severity_counts = state_severity_counts.merge(state_total_counts, on='State')

# Calculate percentages
all_accident_in_range = state_severity_counts['Total_Accidents'].drop_duplicates().sum()

state_severity_counts['Percentage'] = (state_severity_counts['Total_Accidents'] / all_accident_in_range) * 100

# Compute rank based on total accidents
state_total_counts['Rank'] = state_total_counts['Total_Accidents'].rank(ascending=False).astype(int)

# Merge ranks back to the severity-level data
state_severity_counts = state_severity_counts.merge(state_total_counts[['State', 'Rank']], on='State')
state_severity_counts.sort_values('Rank', ascending=True, inplace=True)


# Create the tooltip column
def get_tooltip(row):
    return (
        f"Rank: {row['Rank']}<br>"
        f"State: {row['State']}<br>"
        f"Total Accidents: {row['Total_Accidents']} ({row['Percentage']:.2f}%)<br>"
        
        f"Severity: {row['Severity']}<br>"
        f"Severity Count: {row['Accident_Count']} <br>"
    )

state_severity_counts['Tooltip'] = state_severity_counts.apply(get_tooltip, axis=1)


state_severity_counts = state_severity_counts.head(40)


top10_bar = px.bar(
    state_severity_counts,
    y= "State",
    x = "Accident_Count",
    color='Severity',
    orientation='h',
    custom_data=["Tooltip"],  # Pass tooltip data
    hover_data={"Tooltip"},
    text = None,
    category_orders={"State": state_severity_counts['State'].unique(),
                     "Severity": ['Critical', 'High', 'Medium', 'Low']}
)

top10_bar.for_each_trace(
    lambda trace: trace.update(
        hovertemplate="%{customdata[0]}<extra></extra>"  # Use Tooltip column and remove default hover info
    )
)

top10_bar.update_layout(
    yaxis_title="State",
    xaxis_title="Accident Count",
    barmode="stack",
    height = 400,
    margin={"r": 0, "t": 50, "l": 0, "b": 50},  # Adjust margins for better fit
    legend=dict(
        yanchor="top",
        y=0.33,
        xanchor="right",
        x=0.9
    ),
    # title="Top 10 States Accident Counts and Severity",
    xaxis=dict(range=[0, state_severity_counts["Accident_Count"].max() * 1.8]) 
)





state_yearly_accidents = filtered_data.groupby(['State']).agg({'ID': 'count'}).reset_index()
state_yearly_accidents.columns = ['State','Accident_Count']

# Step 4: Aggregate accident counts by severity for each state and year
state_yearly_severity_counts = filtered_data.groupby(['State', 'Severity']).agg({'ID': 'count'}).reset_index()
state_yearly_severity_counts.columns = ['State', 'Severity', 'Severity_Count']

# Step 5: Merge the total accident counts and severity counts into one DataFrame
state_yearly_data = pd.merge(state_yearly_accidents, state_yearly_severity_counts, on=['State'], how='left')
all_states = [
    "Alabama", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida",
    "Georgia", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
    "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana",
    "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina",
    "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina",
    "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
    "Wisconsin", "Wyoming"
]
all_states_df = pd.DataFrame({"State": all_states})
state_yearly_data = pd.merge(all_states_df, state_yearly_data, on="State", how="left")


# Create the tooltip column with all severity counts
def get_severity_count(state_code, severity):
    # Filter the data for the state and severity
    severity_count = state_yearly_data[(state_yearly_data['State'] == state_code) & 
                                       (state_yearly_data['Severity'] == severity)]
    
    # If the severity count exists, return it; otherwise, return 0
    if not severity_count.empty:
        return severity_count['Severity_Count'].values[0]
    else:
        return 0  # If no data, return 0

# Generate the tooltip for each row
state_yearly_data['tooltip'] = state_yearly_data.apply(
    lambda row: f"Total Accidents: {row['Accident_Count']}<br>"
                f"Low: {get_severity_count(row['State'], 'Low')}<br>"
                f"Medium: {get_severity_count(row['State'], 'Medium')}<br>"
                f"High: {get_severity_count(row['State'], 'High')}<br>"
                f"Critical: {get_severity_count(row['State'], 'Critical')}",
    axis=1)


state_yearly_data = state_yearly_data.sort_values(by=["Accident_Count"], ascending=[False])

from pandas.api.types import CategoricalDtype
severity_order = CategoricalDtype(categories=['Critical', 'High', 'Medium', 'Low'], ordered=True)

# Apply the custom category order to the Severity column
state_yearly_data['Severity'] = state_yearly_data['Severity'].astype(severity_order)


state_yearly_data = state_yearly_data[['State', 'Accident_Count', 'tooltip']].drop_duplicates()
state_yearly_data['Accident_Count'] = state_yearly_data['Accident_Count'].fillna(0)

adjusted_data = state_yearly_data.copy()
adjusted_data.loc[adjusted_data['State'] == 'California', 'Accident_Count'] = min(
    adjusted_data[adjusted_data['State'] != 'California']['Accident_Count'].max() * 1.2,
    adjusted_data.loc[adjusted_data['State'] == 'California', 'Accident_Count'].values[0]
)

geojson_file = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
geojson_data = requests.get(geojson_file).json()

m = folium.Map(location=[37.0902, -95.7129], zoom_start=4, tiles="cartodbpositron")

# Merge the DataFrame into the GeoJSON
for feature in geojson_data["features"]:
    state_name = feature["properties"]["name"]  # GeoJSON state name
    # Match state name and add Accident_Count and tooltip data
    match = state_yearly_data[state_yearly_data["State"] == state_name]
    if not match.empty:
        feature["properties"]["Accident_Count"] = int(match["Accident_Count"].iloc[0])
        feature["properties"]["tooltip"] = match["tooltip"].values[0]
    else:
        feature["properties"]["Accident_Count"] = 0
        feature["properties"]["tooltip"] = "No data available"

folium.Choropleth(
    geo_data=geojson_data,  # GeoJSON data for US states
    data = adjusted_data,  # Data containing accident counts
    columns=["State", "Accident_Count"],  # Columns to match and color by
    key_on="feature.properties.name",  # GeoJSON key to match State_Code (usually in the 'id' field)
    fill_opacity=0.7,
    line_opacity=0.2,
    fill_color="viridis",
    legend_name="Accident Count by State"
).add_to(m)


tooltip = folium.GeoJsonTooltip(
    fields=["name", "tooltip"],
    aliases=["State:", "Severity:"],
    localize=True,
    sticky=True,
    labels=False,
    style="""
        background-color: #F0EFEF;
        border: 2px solid black;
        border-radius: 3px;
        box-shadow: 3px;
    """,
    max_width=800,
)


folium.GeoJson(
    geojson_data,
    tooltip=tooltip
).add_to(m)

with col1:
    st.markdown(f"#### Top 10 State With Severity in {selected_years}")

    st.plotly_chart(top10_bar, use_container_width=True)
    st.markdown(f"#### Top 10 Cities in US with most no. of Road Accident Cases in {selected_years}")

    st_folium(m, width=725,height=400)


city_df = pd.DataFrame(filtered_data['City'].value_counts()).reset_index().rename(columns={'count':'Accident_Count'})
city_df['Percentage'] = city_df['Accident_Count']/city_df["Accident_Count"].sum()*100

top_10_cities = city_df.head(10)

# Create the bar plot
top_10_city_bar = px.bar(
    top_10_cities,
    x="City",
    y="Accident_Count",
    text=top_10_cities["Percentage"].apply(lambda x: f"{x:.2f}%"),  # Add percentage as text
    # title="'\nTop 10 Cities in US with most no. of \nRoad Accident Cases (2016-2020)\n'",
    labels={"Accident_Count": "Accident Count", "City": "City"},
    color="City" # Use Rainbow color sequence
)

# Customize the layout
top_10_city_bar.update_traces(
    textposition="inside",  # Place the percentage text inside the bars
    textfont=dict(
        size=12,  # Font size
        color="white",  # White text
        family="Arial",  # Font family
        weight="bold"  # Bold text
    ),   
    hovertemplate="City: %{x}<br>Accident Count: %{y}<br>Percentage: %{text}<extra></extra>"
)

top_10_city_bar.update_layout(
    xaxis_title="City",
    yaxis_title="Accident Count",
    margin=dict(l=50, r=50, t=50, b=50),
    coloraxis_colorbar=dict(
        title="Accident Count"
    ),
    height = 400
)


selected_city = st.sidebar.selectbox(
    "Select a city to display heatmap:",
    options=top_10_cities["City"].tolist(),
    index=1  # Default to the Los Angeles
)

# Filter the data for the selected city
filtered_cities = filtered_data[filtered_data["City"] == selected_city]
filtered_cities = filtered_cities[['ID', 'Severity', 'Start_Lat', 'Start_Lng']]


heat_data = [[row['Start_Lat'], row['Start_Lng']] for index, row in filtered_cities.iterrows()]
from folium.plugins import HeatMap
def create_heatmap(df_loc, latitude, longitude, zoom =12, tiles='OpenStreetMap'):
    """
    Generate a Folium Map with a heatmap of accident locations.
    """
    # Create a list of coordinates from the dataframe columns 'Start_Lat' and 'Start_Lng'
    heat_data = [[row['Start_Lat'], row['Start_Lng']] for index, row in df_loc.iterrows()]

    # Create a map centered around the specified coordinates
    world_map = folium.Map(location=[latitude, longitude], zoom_start=zoom, tiles=tiles)

    # Add the heatmap layer to the map
    HeatMap(heat_data).add_to(world_map)

    return world_map

map_us_heatmap = create_heatmap(
    filtered_cities, 
    us_cities_coords[selected_city]['lat'],
    us_cities_coords[selected_city]['lon'], 11
)



with col2:
    st.markdown(f"#### Top 10 Cities in US with most no. of Road Accident Cases in {selected_years}")
    st.plotly_chart(top_10_city_bar, use_container_width=True)

    st.markdown(f"#### Heatmap of Accidents in {selected_city}")
    st_folium(map_us_heatmap, width=800, height=400)


