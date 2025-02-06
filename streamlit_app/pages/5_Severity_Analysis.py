import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from folium.features import GeoJsonTooltip
from streamlit_folium import st_folium
from constants import US_CITIES_COORDS
import plotly.express as px
import plotly.graph_objects as go

data = st.session_state.data
severity_counts = data['Severity'].value_counts().sort_index()
severity_percentages = data['Severity'].value_counts(normalize=True).sort_index() * 100

# Create a DataFrame for displaying
severity_df = pd.DataFrame({
    'Severity Level': severity_counts.index,
    'Count': severity_counts.values,
    'Percentage': severity_percentages.values
})
severity_df

col2_1, col2_2, col2_3, col2_4 = st.columns([1, 1, 1, 1])
# Create a metrics
with col2_1:
    st.metric(label = 'Critical Severity', value = severity_counts[0], delta = f"{severity_percentages[0]:.2f}%")
with col2_2:
    st.metric(label = 'High Severity', value = severity_counts[1], delta = f"{severity_percentages[1]:.2f}%")
with col2_3:
    st.metric(label = 'Medium Severity', value = severity_counts[2], delta = f"{severity_percentages[2]:.2f}%")
with col2_4:
    st.metric(label = 'Low Severity', value = severity_counts[3], delta = f"{severity_percentages[3]:.2f}%")
