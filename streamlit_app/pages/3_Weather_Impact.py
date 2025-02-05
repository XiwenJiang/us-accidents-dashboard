import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.title("Weather Impact Analysis")
st.write("Analysis of how weather conditions affect accident frequency and severity.")

# Get data from session state
data = st.session_state.data
weather_columns = ['Temperature(F)', 'Humidity(%)', 'Pressure(in)', 'Visibility(mi)', 'Wind_Direction', 'Wind_Speed(mph)', 'Precipitation(in)', 'Weather_Condition']
road_conditions = ['Bump', 'Crossing', 'Give_Way', 'Junction', 'Stop', 'No_Exit', 'Traffic_Signal', 'Turning_Loop']
weather = data[weather_columns + road_conditions]
weather['Severity'] = data['Severity']
# Count missing values per row for weather columns
missing_per_row = weather[weather_columns].isna().sum(axis=1)

# Update weather DataFrame
weather = weather[missing_per_row < 6]

weather