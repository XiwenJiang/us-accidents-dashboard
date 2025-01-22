import streamlit as st
import pandas as pd
import numpy as np
import pickle
from PIL import Image

st.write("""
         # US Car Accidents App
         The primary objectives of this analysis are to:
            - **Visualize Geographic Data**: Leverage geospatial data to create intuitive and informative visualizations.
            - **Identify Accident Hotspots**: Locate and analyze regions with high frequencies of traffic accidents.
         """)

# Load dataset
@st.cache_data
def load_data():
    data = pd.read_csv('temp/US_Accidents_March23_sampled_500k.csv')
    return data

data = load_data()