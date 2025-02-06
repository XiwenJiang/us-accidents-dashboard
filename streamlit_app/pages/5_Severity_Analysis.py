import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from folium.features import GeoJsonTooltip
from streamlit_folium import st_folium
from constants import US_CITIES_COORDS
import plotly.express as px
import plotly.graph_objects as go

box_template = """
<div style="background:{}; padding:15px; border-radius:10px; text-align:center; color:white; font-size:18px;">
    <b>{}</b><br>
    <span style="font-size:24px;">{}</span><br>
    <span style="font-size:14px;">Δ {}</span>
</div>
"""

colors = ["#FF5733", "#FF8C00", "#FFD700", "#28A745"]  # 红，橙，黄，绿


data = st.session_state.data

def severity_data(data):
    """Get severity data"""
    severity_counts = data['Severity'].value_counts().sort_index()
    severity_percentages = data['Severity'].value_counts(normalize=True).sort_index() * 100

    # Create a DataFrame for displaying
    severity_df = pd.DataFrame({
        'Severity Level': severity_counts.index,
        'Count': severity_counts.values,
        'Percentage': severity_percentages.values
    })
    return severity_df
severity_df = severity_data(data)

severity_df

col1, col2, col3 = st.columns((0.3, 0.4, 0.3), gap ='small')

with col2:
    # Display the severity data
    col2_1, col2_2, col2_3, col2_4 = st.columns([1, 1, 1, 1])
    with col2_1:
        st.markdown(box_template.format(colors[0], "Critical", severity_df['Count'][0], f"{severity_df['Percentage'][0]:.2f}%"), unsafe_allow_html=True)
        
    with col2_2:
        st.markdown(box_template.format(colors[1], "High", severity_df['Count'][1], f"{severity_df['Percentage'][1]:.2f}%"), unsafe_allow_html=True)
        
    with col2_3:
        st.markdown(box_template.format(colors[2], "Medium", severity_df['Count'][3], f"{severity_df['Percentage'][3]:.2f}%"), unsafe_allow_html=True)
        
    with col2_4:
        st.markdown(box_template.format(colors[3], "Low", severity_df['Count'][2], f"{severity_df['Percentage'][2]:.2f}%"), unsafe_allow_html=True)

# Plot the severity data on us map
