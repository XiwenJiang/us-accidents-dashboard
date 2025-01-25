import streamlit as st
import pandas as pd

st.title("State Analysis")
st.write("Explore accident data by state.")
st.write("This page will include state-specific statistics and visualizations.")

data = st.session_state.data
#st.write(data.head())


state_yearly_accidents = data.groupby(['State_Code', 'Year']).agg({'ID': 'count'}).reset_index()
state_yearly_accidents.columns = ['State_Code', 'Year', 'Accident_Count']

state_yearly_severity_counts = data.groupby(['State_Code', 'Year', 'Severity']).agg({'ID': 'count'}).reset_index()
state_yearly_severity_counts.columns = ['State_Code', 'Year', 'Severity', 'Severity_Count']

state_yearly_data = pd.merge(state_yearly_accidents, state_yearly_severity_counts, on=['State_Code', 'Year'], how='left')

def get_severity_count(state_code, severity):
    # Filter the data for the state and severity
    severity_count = state_yearly_data[(state_yearly_data['State_Code'] == state_code) & 
                                       (state_yearly_data['Severity'] == severity)]
    
    # If the severity count exists, return it; otherwise, return 0
    if not severity_count.empty:
        return severity_count['Severity_Count'].values[0]
    else:
        return 0  # If no data, return 0

# Generate the tooltip for each row
state_yearly_data['tooltip'] = state_yearly_data.apply(
    lambda row: f"State: {row['State_Code']}<br>Total Accidents: {row['Accident_Count']}<br>"
                f"Low: {get_severity_count(row['State_Code'], 'Low')}<br>"
                f"Medium: {get_severity_count(row['State_Code'], 'Medium')}<br>"
                f"High: {get_severity_count(row['State_Code'], 'High')}<br>"
                f"Critical: {get_severity_count(row['State_Code'], 'Critical')}",
    axis=1)



st.write(state_yearly_data.head())
st.write(state_yearly_accidents.info())