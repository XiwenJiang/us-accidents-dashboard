import streamlit as st
import plotly.express as px
import pandas as pd
st.title("Welcome to the US Accidents Dashboard!")


# Create the layout with two columns
col1, col2 = st.columns([1, 2])  # Adjust the width ratio (e.g., 1:2 for left:right)

with col1:
    st.title("US Accidents Dashboard")
    st.subheader("Project Overview")
    st.write("""
        This dashboard provides an in-depth analysis of US traffic accidents.
        Our goal is to uncover patterns in accident data and provide actionable insights.
        
        **Key Features:**
        - Explore accident trends over time.
        - Analyze accident distribution across states.
        - Visualize accident hotspots with interactive maps.
        
        The data used in this dashboard is sourced from the [US Accident Dataset](https://www.kaggle.com/sobhanmoosavi/us-accidents).
        """)


# Right Column: US Map with Plotly
with col2:
    st.subheader("Interactive US Map")
    st.write("This map shows accident locations across the United States.")

    # Example dataset: Create a random sample of US accident data
    data = pd.DataFrame({
        'Latitude': [37.7749, 40.7128, 34.0522, 41.8781, 29.7604],
        'Longitude': [-122.4194, -74.0060, -118.2437, -87.6298, -95.3698],
        'City': ['San Francisco', 'New York', 'Los Angeles', 'Chicago', 'Houston']
    })

    # Generate a Plotly scatter mapbox
    fig = px.scatter_mapbox(
        data,
        lat="Latitude",
        lon="Longitude",
        hover_name="City",
        zoom=3,
        title="US Accident Locations"
    )

    # Mapbox style (use 'carto-positron' for a clean look)
    fig.update_layout(mapbox_style="carto-positron")

    # Display the Plotly figure
    st.plotly_chart(fig, use_container_width=True)
