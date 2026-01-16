import streamlit as st
import plotly.express as px
import pandas as pd
from constants import STATE_COORDINATES
st.set_page_config(layout="wide")
S3_BASE = "s3://us-accidents-dashboard-1445/processed"

@st.cache_data(ttl=3600)
def load_table(name: str) -> pd.DataFrame:
    return pd.read_parquet(f"{S3_BASE}/{name}/")


@st.cache_data(ttl=3600)
def build_state_yearly_data() -> pd.DataFrame:
    df = load_table("state_yearly_summary")

    # 经纬度（小表映射，极快）
    df["Latitude"] = df["State_Code"].map(lambda x: STATE_COORDINATES[x][0])
    df["Longitude"] = df["State_Code"].map(lambda x: STATE_COORDINATES[x][1])

    # tooltip（O(N) 字符串拼接，不再做嵌套过滤）
    df["tooltip"] = (
        "State: " + df["State_Code"].astype(str) + "<br>"
        "Total Accidents: " + df["Accident_Count"].astype(int).astype(str) + "<br>"
        "Low: " + df["Low"].astype(int).astype(str) + "<br>"
        "Medium: " + df["Medium"].astype(int).astype(str) + "<br>"
        "High: " + df["High"].astype(int).astype(str) + "<br>"
        "Critical: " + df["Critical"].astype(int).astype(str)
    )
    return df

state_yearly_data = build_state_yearly_data()



st.title("Welcome to the US Accidents Dashboard!")


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
