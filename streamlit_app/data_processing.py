import pandas as pd
import streamlit as st
from constants import US_STATES

@st.cache_data
def process_yearly_data(data):
    """Process data to get yearly statistics"""
    state_yearly_accidents = data.groupby(['State_Code', 'Year']).agg({'ID': 'count'}).reset_index()
    state_yearly_accidents.columns = ['State_Code', 'Year', 'Accident_Count']
    
    state_yearly_severity_counts = data.groupby(['State_Code', 'Year', 'Severity']).agg({'ID': 'count'}).reset_index()
    state_yearly_severity_counts.columns = ['State_Code', 'Year', 'Severity', 'Severity_Count']
    
    return pd.merge(state_yearly_accidents, state_yearly_severity_counts, 
                   on=['State_Code', 'Year'], how='left')

@st.cache_data
def get_city_statistics(data):
    """Process city-level statistics"""
    city_df = pd.DataFrame(data['City'].value_counts()).reset_index()
    city_df.columns = ['City', 'Accident_Count']
    city_df['Percentage'] = city_df['Accident_Count']/city_df["Accident_Count"].sum()*100
    return city_df

@st.cache_data
def get_filtered_data(data, selected_years):
    """Filter data based on selected years"""
    if '2016-2023' not in selected_years:
        return data[data['Year'].isin(selected_years)]
    return data
