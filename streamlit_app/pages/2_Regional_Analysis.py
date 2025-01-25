import streamlit as st
import pandas as pd
import plotly.express as px

st.title("State Analysis")
st.write("Explore accident data by state.")
st.write("This page will include state-specific statistics and visualizations.")

data = st.session_state.data

# Aggregate accident counts by State and Severity
state_severity_counts = data.groupby(['State', 'Severity']).agg({'ID': 'count'}).reset_index()
state_severity_counts.columns = ['State', 'Severity', 'Accident_Count']

# Compute total counts for each state and percentages
state_total_counts = data.groupby('State').agg({'ID': 'count'}).reset_index()
state_total_counts.columns = ['State', 'Total_Accidents']

# Merge total counts back to the severity-level data
state_severity_counts = state_severity_counts.merge(state_total_counts, on='State')

# Calculate percentages
state_severity_counts['Percentage'] = (state_severity_counts['Accident_Count'] / state_severity_counts['Total_Accidents']) * 100

# Compute rank based on total accidents
state_total_counts['Rank'] = state_total_counts['Total_Accidents'].rank(ascending=False).astype(int)

# Merge ranks back to the severity-level data
state_severity_counts = state_severity_counts.merge(state_total_counts[['State', 'Rank']], on='State')
state_severity_counts.sort_values('Rank', ascending=True, inplace=True)


# Create the tooltip column
def get_tooltip(row):
    return (
        f"State: {row['State']}<br>"
        f"Total Accidents: {row['Total_Accidents']}<br>"
        f"Rank: {row['Rank']}<br>"
        f"Severity: {row['Severity']}<br>"
        f"Accident Count: {row['Accident_Count']} ({row['Percentage']:.2f}%)<br>"
    )

state_severity_counts['Tooltip'] = state_severity_counts.apply(get_tooltip, axis=1)
state_severity_counts


fig = px.bar(
    state_severity_counts,
    y= "State",
    x = "Accident_Count",
    color='Severity',
    orientation='h',
    custom_data=["Tooltip"],  # Pass tooltip data
    hover_data={"Tooltip"},
    category_orders={"State": state_severity_counts['State'].unique()}
)

fig.update_layout(
    yaxis_title="State",
    xaxis_title="Accident Count",
    height = 1000,
    xaxis_tickangle=45,  # Rotate x-axis labels for readability
    margin={"r": 0, "t": 50, "l": 0, "b": 50}  # Adjust margins for better fit
)


st.plotly_chart(fig, use_container_width=True)
