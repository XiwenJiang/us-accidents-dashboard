import streamlit as st
import pandas as pd
import numpy as np
import pickle
from PIL import Image
import folium
from folium.plugins import MarkerCluster
import geopandas as gpd
from streamlit_folium import st_folium 
import plotly.express as px
import plotly.graph_objects as go

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
    data['Start_Time'] = pd.to_datetime(data['Start_Time'].str.replace(r'\.\d+$', '', regex=True), errors='coerce')
    data['End_Time'] = pd.to_datetime(data['End_Time'].str.replace(r'\.\d+$', '', regex=True), errors='coerce')
    data['Year'] = data['Start_Time'].dt.year
    data['Month'] = data['Start_Time'].dt.month
    data['Day of Week'] = data['Start_Time'].dt.dayofweek
    data['Hour'] = data['Start_Time'].dt.hour

    # Severity Levels
    severity_level = {1: 'Low', 2: 'Medium', 3: 'High', 4: 'Critical'}
    data['Severity'] = data['Severity'].map(severity_level)

    # State Code
    data['State_Code'] = data['State']
    data['State'] = data['State_Code'].apply(state_code)

    return data

data = load_data()

st.write(data.head())

# Display the map in Streamlit using st_folium
st.write("### Accident Locations on the Map")
state_yearly_accidents = data.groupby(['State_Code', 'Year']).agg({'ID': 'count'}).reset_index()
state_yearly_accidents.columns = ['State_Code', 'Year', 'Accident_Count']

# Step 4: Aggregate accident counts by severity for each state and year
state_yearly_severity_counts = data.groupby(['State_Code', 'Year', 'Severity']).agg({'ID': 'count'}).reset_index()
state_yearly_severity_counts.columns = ['State_Code', 'Year', 'Severity', 'Severity_Count']

# Step 5: Merge the total accident counts and severity counts into one DataFrame
state_yearly_data = pd.merge(state_yearly_accidents, state_yearly_severity_counts, on=['State_Code', 'Year'], how='left')

# Step 6: Create the tooltip column with all severity counts
def get_severity_count(state_code, severity):
    # Filter the data for the state and severity
    severity_count = state_yearly_data[(state_yearly_data['State_Code'] == state_code) & 
                                       (state_yearly_data['Severity'] == severity)]
    
    # If the severity count exists, return it; otherwise, return 0
    if not severity_count.empty:
        return severity_count['Severity_Count'].values[0]
    else:
        return 0  # If no data, return 0

# Generate the tooltip for each row
state_yearly_data['tooltip'] = state_yearly_data.apply(
    lambda row: f"State: {row['State_Code']}<br>Total Accidents: {row['Accident_Count']}<br>"
                f"Low: {get_severity_count(row['State_Code'], 'Low')}<br>"
                f"Medium: {get_severity_count(row['State_Code'], 'Medium')}<br>"
                f"High: {get_severity_count(row['State_Code'], 'High')}<br>"
                f"Critical: {get_severity_count(row['State_Code'], 'Critical')}",
    axis=1)

fig = px.scatter_geo(state_yearly_data,
                    locations='State_Code',
                    locationmode='USA-states',
                    color='Accident_Count',
                    hover_name='State_Code',
                    color_continuous_scale='Plasma',
                    size = 'Accident_Count',
                    animation_frame="Year",
                    labels={'Accident_Count': 'Number of Accidents'},
                    title='Accident Locations by State on the Map',
                    hover_data={'tooltip': True},
                    template="plotly",
                    size_max=60)


# Step 8: Update the map style and settings
fig.update_geos(scope='usa',
            projection_type='albers usa',

            showcoastlines=True,
            coastlinecolor='Gray',
            lataxis_showgrid=True, lonaxis_showgrid=True,
            showsubunits=True,
            showlakes = True)

st.plotly_chart(fig)




# Step 5: Generate animation frames for each year
frames = [
    go.Frame(
        data=[go.Scattergeo(
            locationmode='USA-states',
            locations=state_yearly_data[state_yearly_data['Year'] == year]['State_Code'],
            text=state_yearly_data[state_yearly_data['Year'] == year]['tooltip'],
            hoverinfo='text',
            marker=dict(
                size=state_yearly_data[state_yearly_data['Year'] == year]['Accident_Count'] / 100,  # Scaling for visibility
                color=state_yearly_data[state_yearly_data['Year'] == year]['Accident_Count'],
                colorscale='Plasma',
                colorbar_title='Accident Count',
                line=dict(width=0)
            )
        )],
        name=str(year)  # The frame name is the year
    )
    for year in state_yearly_data['Year'].unique()
]

# Step 6: Create the Scattergeo plot with animation
fig = go.Figure(
    data=[go.Scattergeo(
        locationmode='USA-states',
        locations=state_yearly_data[state_yearly_data['Year'] == state_yearly_data['Year'].min()]['State_Code'],
        text=state_yearly_data[state_yearly_data['Year'] == state_yearly_data['Year'].min()]['tooltip'],
        hoverinfo='text',
        marker=dict(
            size=state_yearly_data[state_yearly_data['Year'] == state_yearly_data['Year'].min()]['Accident_Count'] / 100,
            color=state_yearly_data[state_yearly_data['Year'] == state_yearly_data['Year'].min()]['Accident_Count'],
            colorscale='Plasma',
            colorbar_title='Accident Count',
            line=dict(width=0)
        )
    )],
    frames=frames  # Add the frames to the figure
)

# Step 7: Add animation control buttons
fig.update_layout(
    updatemenus=[
        dict(
            type='buttons',
            showactive=True,
            buttons=[
                dict(
                    label='Play',
                    method='animate',
                    args=[None, dict(frame=dict(duration=500, redraw=True), fromcurrent=True)]  # Play the animation
                ),
                dict(
                    label='Pause',
                    method='animate',
                    args=[None, dict(frame=dict(duration=0, redraw=False), mode='immediate')]  # Pause the animation
                )
            ],
            direction='left',
            pad={'r': 10, 't': 87},

            x=0.1,
            xanchor='right',
            y=0,
            yanchor='top'
        )
    ],
    geo=dict(
        scope='usa',
        projection_type='albers usa',
        showcoastlines=True,
        coastlinecolor='Black',
        showsubunits=True
    ),
    title='Accidents by State Over Time'
)

# Step 8: Display the map in Streamlit
st.plotly_chart(fig, use_container_width=True)

