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

import pandas as pd
import numpy as np
from constants import US_STATES

def state_code(state_code): 
    return US_STATES[state_code]

def load_data(file_url):
    # Load and process data
    data = pd.read_csv(file_url)

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
    # Integrate datetime columns
    data['Start_Time'] = pd.to_datetime(data['Start_Time'].str.replace(r'\.\d+$', '', regex=True), errors='coerce')
    data['End_Time'] = pd.to_datetime(data['End_Time'].str.replace(r'\.\d+$', '', regex=True), errors='coerce')
    data['Year'] = data['Start_Time'].dt.year
    data['Month'] = data['Start_Time'].dt.month
    data['Day of Week'] = data['Start_Time'].dt.dayofweek
    data['Hour'] = data['Start_Time'].dt.hour
    data['Quarter'] = data['Start_Time'].dt.quarter
    data['YearQuarter'] = data['Year'].astype(str) + '-Q' + data['Quarter'].astype(str)

    # Severity Levels
    severity_level = {1: 'Low', 2: 'Medium', 3: 'High', 4: 'Critical'}
    data['Severity'] = data['Severity'].map(severity_level)

    # State Code
    data['State_Code'] = data['State']
    data['State'] = data['State_Code'].apply(state_code)

    return data

def get_weather_data(data):
    weather_columns = ['Temperature(F)', 'Humidity(%)', 'Pressure(in)', 'Visibility(mi)', 
                      'Wind_Direction', 'Wind_Speed(mph)', 'Precipitation(in)', 'Weather_Condition']
    road_conditions = ['Bump', 'Crossing', 'Give_Way', 'Junction', 'Stop', 'No_Exit', 'Traffic_Signal']
    weather = data[weather_columns + road_conditions]
    weather['Severity'] = data['Severity']
    
    # Remove rows with too many missing values
    missing_per_row = weather[weather_columns].isna().sum(axis=1)
    weather = weather[missing_per_row < 6]
    
    return weather

def get_severity_data(data):
    severity_counts = data['Severity'].value_counts().sort_index()
    severity_percentages = data['Severity'].value_counts(normalize=True).sort_index() * 100

    severity_df = pd.DataFrame({
        'Severity Level': severity_counts.index,
        'Count': severity_counts.values,
        'Percentage': severity_percentages.values
    })
    return severity_df
