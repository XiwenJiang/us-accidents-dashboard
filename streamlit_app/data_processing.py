import pandas as pd
import streamlit as st
from constants import US_STATES, ALL_STATES, STATE_COORDINATES


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

@st.cache_data
def get_state_severity_data(filtered_data):
    """Process state severity data"""
    # Aggregate accident counts by State and Severity
    state_severity_counts = filtered_data.groupby(['State', 'Severity']).agg({'ID': 'count'}).reset_index()
    state_severity_counts.columns = ['State', 'Severity', 'Accident_Count']

    # Compute total counts for each state
    state_total_counts = filtered_data.groupby('State').agg({'ID': 'count'}).reset_index()
    state_total_counts.columns = ['State', 'Total_Accidents']

    # Merge and calculate percentages
    state_severity_counts = state_severity_counts.merge(state_total_counts, on='State')
    all_accidents = state_severity_counts['Total_Accidents'].drop_duplicates().sum()
    state_severity_counts['Percentage'] = (state_severity_counts['Total_Accidents'] / all_accidents) * 100

    # Add rank
    state_total_counts['Rank'] = state_total_counts['Total_Accidents'].rank(ascending=False).astype(int)
    state_severity_counts = state_severity_counts.merge(
        state_total_counts[['State', 'Rank']], 
        on='State'
    ).sort_values('Rank', ascending=True)

    return state_severity_counts

@st.cache_data
def get_temporal_data(filtered_data):
    """Process temporal analysis data"""
    # Get accidents by year and severity
    accidents_per_year_severity = filtered_data.groupby(['Year', 'Severity']).size().reset_index(name='Count')
    
    # Get total accidents per year
    accidents_per_year = filtered_data.groupby('Year').size().reset_index(name='Total_Count')
    
    # Get accidents by month
    filtered_data['YearMonth'] = pd.to_datetime(filtered_data['Start_Time'].dt.strftime('%Y-%m'))
    accidents_per_month = filtered_data.groupby('YearMonth').size().reset_index(name='Count')
    
    # Get accidents by weekday
    accidents_per_weekday = filtered_data.groupby('Day of Week').size().reset_index(name='Total_Count')
    
    # Get accidents by hour
    accidents_per_hour = filtered_data.groupby('Hour').size().reset_index(name='Total_Count')
    
    return {
        'yearly_severity': accidents_per_year_severity,
        'yearly_total': accidents_per_year,
        'monthly': accidents_per_month,
        'weekday': accidents_per_weekday,
        'hourly': accidents_per_hour
    }

@st.cache_data
def get_top_10_states_by_quarter(data):
    """Get top 10 states for each quarter"""
    state_time_counts = data.groupby(['State', 'Year', 'Quarter', 'YearQuarter'])['ID'].count().reset_index(name='Count')
    
    top_10_states = (state_time_counts.groupby('YearQuarter')
                    .apply(lambda x: x.nlargest(10, 'Count')
                          .sort_values('Count', ascending=True))
                    .reset_index(drop=True))
    
    severity_counts = (data.groupby(['State', 'YearQuarter', 'Severity'])
                      .size()
                      .reset_index(name='Severity_Count'))
    
    return top_10_states, severity_counts

@st.cache_data
def get_racing_bar_tooltip(state, yearquarter, severity_counts):
    """Generate tooltip for racing bar chart"""
    state_data = severity_counts[(severity_counts['State'] == state) & 
                               (severity_counts['YearQuarter'] == yearquarter)]
    tooltip = f"State: {state}<br>"
    tooltip += f"Time: {yearquarter}<br>"
    total = state_data['Severity_Count'].sum()
    tooltip += f"Total Accidents: {total}<br>"
    
    for _, row in state_data.iterrows():
        pct = (row['Severity_Count'] / total * 100)
        tooltip += f"{row['Severity']}: {row['Severity_Count']} ({pct:.1f}%)<br>"
    
    return tooltip

@st.cache_data
def get_state_analysis_data(filtered_data):
    """Process state-level analysis data"""
    # Aggregate accident counts by State and Severity
    state_severity_counts = filtered_data.groupby(['State', 'Severity']).agg({'ID': 'count'}).reset_index()
    state_severity_counts.columns = ['State', 'Severity', 'Accident_Count']

    # Compute total counts and percentages
    state_total_counts = filtered_data.groupby('State').agg({'ID': 'count'}).reset_index()
    state_total_counts.columns = ['State', 'Total_Accidents']
    
    # Merge and calculate statistics
    state_severity_counts = state_severity_counts.merge(state_total_counts, on='State')
    all_accident_in_range = state_severity_counts['Total_Accidents'].drop_duplicates().sum()
    state_severity_counts['Percentage'] = (state_severity_counts['Total_Accidents'] / all_accident_in_range) * 100
    
    # Add rank
    state_total_counts['Rank'] = state_total_counts['Total_Accidents'].rank(ascending=False).astype(int)
    state_severity_counts = state_severity_counts.merge(
        state_total_counts[['State', 'Rank']], 
        on='State'
    ).sort_values('Rank', ascending=True)
    
    return state_severity_counts.head(40)

@st.cache_data  # 修复了 @st.cache_datdef 的拼写错误
def get_state_yearly_data(filtered_data):
    """Process state yearly data with severity counts"""
    # Get basic accident counts
    state_yearly_accidents = filtered_data.groupby(['State']).agg({'ID': 'count'}).reset_index()
    state_yearly_accidents.columns = ['State', 'Accident_Count']
    
    # Get severity counts
    state_yearly_severity = filtered_data.groupby(['State', 'Severity']).agg({'ID': 'count'}).reset_index()
    state_yearly_severity.columns = ['State', 'Severity', 'Severity_Count']
    
    # Merge data
    state_yearly_data = pd.merge(state_yearly_accidents, state_yearly_severity, on=['State'], how='left')
    all_states_df = pd.DataFrame({"State": ALL_STATES})
    state_yearly_data = pd.merge(all_states_df, state_yearly_data, on="State", how="left")
    
    # Generate tooltip
    def get_state_tooltip(group):
        tooltip = f"Total Accidents: {group['Accident_Count'].iloc[0]}<br>"
        for severity in ['Low', 'Medium', 'High', 'Critical']:
            count = group[group['Severity'] == severity]['Severity_Count'].sum()
            tooltip += f"{severity}: {count}<br>"
        return tooltip
    
    # Add tooltip column
    state_yearly_data['tooltip'] = state_yearly_data.groupby('State').apply(get_state_tooltip)
    
    return state_yearly_data

@st.cache_data
def create_geojson_data(state_yearly_data, geojson_data):
    """Process and merge data with GeoJSON"""
    for feature in geojson_data["features"]:
        state_name = feature["properties"]["name"]
        match = state_yearly_data[state_yearly_data["State"] == state_name]
        if not match.empty:
            feature["properties"]["Accident_Count"] = int(match["Accident_Count"].iloc[0])
            feature["properties"]["tooltip"] = match["tooltip"].values[0]
        else:
            feature["properties"]["Accident_Count"] = 0
            feature["properties"]["tooltip"] = "No data available"
    return geojson_data

def get_tooltip(row):
    """Generate tooltip for state data"""
    return (
        f"Rank: {row['Rank']}<br>"
        f"State: {row['State']}<br>"
        f"Total Accidents: {row['Total_Accidents']} ({row['Percentage']:.2f}%)<br>"
        f"Severity: {row['Severity']}<br>"
        f"Severity Count: {row['Accident_Count']} <br>"
    )

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
