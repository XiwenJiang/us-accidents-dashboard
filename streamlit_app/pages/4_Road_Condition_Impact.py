
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy.stats import gaussian_kde
from plotly.subplots import make_subplots

st.title("Road Condition Impact Analysis")
st.write("Analysis of how road conditions affect accident frequency and severity.")

# Get data from session state
data = st.session_state.data
weather_columns = ['Temperature(F)', 'Humidity(%)', 'Pressure(in)', 'Visibility(mi)', 'Wind_Direction', 'Wind_Speed(mph)', 'Precipitation(in)', 'Weather_Condition']
road_conditions = ['Bump', 'Crossing', 'Give_Way', 'Junction', 'Stop', 'No_Exit', 'Traffic_Signal', 'Turning_Loop']
weather = data[weather_columns + road_conditions]
weather['Severity'] = data['Severity']


def create_road_condition_pies(data, condition):
    # Create subplots
    fig = make_subplots(rows=1, cols=2, 
                        specs=[[{'type':'pie'}, {'type':'pie'}]],
                        subplot_titles=[f'{condition} Not Present', f'{condition} Present'])
    
    # Colors for severity levels
    colors = px.colors.qualitative.Set2
    severity_order = ['Critical', 'High', 'Medium', 'Low']
    
    # Create pie chart for condition = 0
    condition_0 = data[data[condition] == 0].groupby('Severity').size()
    fig.add_trace(
        go.Pie(labels=severity_order,
               values=[condition_0.get(sev, 0) for sev in severity_order],
               name='Not Present',
               marker_colors=colors,
               hole=0.4),  # Add hole parameter
        row=1, col=1
    )
    
    # Create pie chart for condition = 1
    condition_1 = data[data[condition] == 1].groupby('Severity').size()
    fig.add_trace(
        go.Pie(labels=severity_order,
               values=[condition_1.get(sev, 0) for sev in severity_order],
               name='Present',
               marker_colors=colors,
               hole=0.4),  # Add hole parameter
        row=1, col=2
    )
    
    # Update layout
    fig.update_layout(
        title=f'Severity Distribution by {condition}',
        showlegend=True,
        height=400,
        width=800
    )
    
    return fig


# Create and display pie charts for each road condition
for condition in road_conditions:
    fig = create_road_condition_pies(weather, condition)
    st.plotly_chart(fig)
