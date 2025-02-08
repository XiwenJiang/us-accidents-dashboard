import os
import streamlit as st
import plotly.express as px
import pandas as pd
import requests
from constants import US_STATES, STATE_COORDINATES
from data_processing import load_data

file_url = "https://media.githubusercontent.com/media/XiwenJiang/us-accidents-dashboard/main/US_Accidents_March23_sampled_500k.csv"

st.set_page_config(layout="wide",
                   page_title="US Accidents Dashboard",
                   page_icon=":car:",
                   initial_sidebar_state="auto")

# Load dataset
@st.cache_data
def load_cached_data():
    return load_data(file_url)

st.session_state.data = load_cached_data()

@st.cache_data
def state_yearly_data(data):
    state_yearly_accidents = data.groupby(['State_Code', 'Year']).agg({'ID': 'count'}).reset_index()
    state_yearly_accidents.columns = ['State_Code', 'Year', 'Accident_Count']

    # Step 4: Aggregate accident counts by severity for each state and year
    state_yearly_severity_counts = data.groupby(['State_Code', 'Year', 'Severity']).agg({'ID': 'count'}).reset_index()
    state_yearly_severity_counts.columns = ['State_Code', 'Year', 'Severity', 'Severity_Count']

    # Step 5: Merge the total accident counts and severity counts into one DataFrame
    state_yearly_data = pd.merge(state_yearly_accidents, state_yearly_severity_counts, on=['State_Code', 'Year'], how='left')


    # Map state codes to lat/lon
    state_yearly_data['Latitude'] = state_yearly_data['State_Code'].map(lambda x: STATE_COORDINATES[x][0])
    state_yearly_data['Longitude'] = state_yearly_data['State_Code'].map(lambda x: STATE_COORDINATES[x][1])

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
    return state_yearly_data
state_yearly_data = state_yearly_data(st.session_state.data)



st.title("Welcome to the US Accidents Dashboard!")
data = st.session_state.data

st.subheader("Project Description")
st.write("""
    This project focuses on conducting an in-depth visual analysis of traffic accidents to identify accident hotspots, 
    examine casualty trends, uncover patterns, and derive cause-and-effect relationships. The study leverages a 
    large-scale dataset containing approximately 3.5 million traffic accident records across the contiguous United 
    States over the past five years. Each record includes a wide range of attributes, such as location, time, weather 
    conditions, natural language descriptions, points-of-interest, and other contextual factors.
# """)

# seperate page into 2 column, left column is project description, and right column is map
col2, col1= st.columns([1, 1.2])



# Create the scatter_mapbox figure
fig = px.scatter_mapbox(
    state_yearly_data,
    lat="Latitude",  # Fixed: Changed from " " to "Latitude"
    lon="Longitude",
    color="Accident_Count",
    size="Accident_Count",
    hover_name="State_Code",
    hover_data={
        "tooltip": True,  # Tooltip column
        "Latitude": False,  # Hide raw latitude in hover
        "Longitude": False,  # Hide raw longitude in hover
    },
    animation_frame="Year",
    color_continuous_scale="Plasma",
    size_max=80,
    title="Accident Locations by State on the Map",
)

# Update mapbox style and layout
fig.update_layout(
    coloraxis_colorbar=dict(
        orientation="h",  # Horizontal color bar
        yanchor="bottom",  # Align to bottom
        y=-0.15,            # Move below the map
        xanchor="center",  # Center horizontally
        x=0.5,             # Center position
        title="Accident Count",  # Title for the color scale
    ),
    mapbox_style="carto-positron",  # Map style
    mapbox_zoom=2,
    mapbox_center={"lat": 37.0902, "lon": -95.7129},  # Centered on the USA
    margin={"r": 0, "t": 50, "l": 0, "b": 0},  # Remove extra margins
    height=600,  # Increase the height
    width=1000  # Increase the width

)

with col1:
    # Display the map in Streamlit
    st.plotly_chart(fig, use_container_width=True)


with col2:
    st.subheader("Study Goals")
    st.write("""
        The primary objective of this study is to raise awareness about traffic safety and highlight the importance of 
        preventive measures. Using intuitive and interactive visualizations, I aim to shed light on accident trends, 
        identify the underlying causes, and evaluate the impact of traffic-calming measures. By showcasing these insights, 
        my goal is to propose actionable solutions to improve public safety, optimize transportation systems, and ultimately 
        reduce the frequency and severity of traffic accidents.
    """)

    st.subheader("Research Questions:")
    st.write("""
        In order to accomplish my goal from this study, I am attempting to answer the folowing questions:         
        1. What are the top 10 states with highest number of traffic accidents?       
        2. Why the number of traffic accidents is high in those states?       
        3. How does the severity level differ in those states?
        4. Where the most traffic accidents happen in different geographic levels (Region, State, City, Airport code, and Zipcode)? 
        5. What is the impact of weather conditions on the number of traffic accidents?
        6. What is the impact of traffic calming, traffic signal, traffic bump, and traffic loop on the number of accidents?
        7. What effect do different time scales have on traffic accidents?
    """)
