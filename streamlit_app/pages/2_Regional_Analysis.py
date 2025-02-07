import streamlit as st
import pandas as pd
import plotly.express as px
import folium
import requests
from folium.features import GeoJsonTooltip

from streamlit_folium import st_folium
from constants import US_CITIES_COORDS, US_STATES, STATE_COORDINATES, ALL_STATES  # 添加 ALL_STATES
from data_processing import (
    get_state_analysis_data,
    get_state_yearly_data,
    create_geojson_data,
    get_city_statistics,
    get_tooltip
)

st.title("Location Analysis")
# st.write("""
#          In this dataset, we have different attributes like City, State, Timezone
#          and even street for each accident records. Here we will analyze these four
#          features based on the no. of cases for each distinct location.
#          """)

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

# Get processed state data
state_severity_counts = get_state_analysis_data(filtered_data)
state_severity_counts['Tooltip'] = state_severity_counts.apply(get_tooltip, axis=1)

# Create state bar chart
top10_bar = px.bar(
    state_severity_counts,
    y="State",
    x="Accident_Count",
    color='Severity',
    orientation='h',
    custom_data=["Tooltip"],
    hover_data={"Tooltip"},
    text=None,
    category_orders={
        "State": state_severity_counts['State'].unique(),
        "Severity": ['Critical', 'High', 'Medium', 'Low']
    }
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

# Get state yearly data
state_yearly_data = get_state_yearly_data(filtered_data)
state_yearly_data = state_yearly_data.sort_values(by=["Accident_Count"], ascending=[False])

# Process GeoJSON data
geojson_file = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
geojson_data = requests.get(geojson_file).json()
geojson_data = create_geojson_data(state_yearly_data, geojson_data)

# Create map
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
    data=state_yearly_data,  # Changed from adjusted_data to state_yearly_data
    columns=["State", "Accident_Count"],
    key_on="feature.properties.name",
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
    
    st.markdown(f"#### Accident Location by State in {selected_years}")

    st_folium(m, width=725,height=400, returned_objects=[])


# Process city data
city_df = get_city_statistics(filtered_data)
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
        family="Arial"  # Font family
        # Removed the weight property as it's not supported
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




with col2:
    st.markdown(f"#### Top 10 Cities in US with most no. of Road Accident Cases in {selected_years}")
    st.plotly_chart(top_10_city_bar, use_container_width=True)
    
    selected_city = st.selectbox(
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
        US_CITIES_COORDS[selected_city]['lat'],
        US_CITIES_COORDS[selected_city]['lon'], 11
    )


    st.markdown(f"#### Heatmap of Accidents in {selected_city}")
    st_folium(map_us_heatmap, width=800, height=400)

st.subheader("Insights:")
st.write("""
         1. In US, :blue[California] is the state :blue[with highest no. of road accidents] in past 5 years.
         2. About :blue[30%] of the total accident records of past 5 years in US is only from :blue[California].
         3. Florida is the 2nd highest (10% cases) state for no. road accidents in US.
         4. :blue[Miami] is the city with :blue[highest (2.42%)] no. of road accidents in US (2016-2020).
         5. Around :blue[14%] accident records of past 5 years are only from these :blue[10 cities] out of 10,657 cities in US (as per the dataset).
         """)