import streamlit as st
import pandas as pd
import plotly.express as px
import folium
import requests
from folium.features import GeoJsonTooltip

from streamlit_folium import st_folium



st.title("State Analysis")
st.write("Explore accident data by state.")
st.write("This page will include state-specific statistics and visualizations.")

data = st.session_state.data

st.sidebar.title("Select Filters")
years = data['Year'].unique().tolist()
years.sort()
years.insert(0, 'All Years')
selected_years = st.sidebar.multiselect(
    "Select Year", years, default=years[0]  # Default to all years
)

if 'All Years' not in selected_years:
    filtered_data = data[data['Year'].isin(selected_years)]
else:
    filtered_data = data



# Aggregate accident counts by State and Severity
state_severity_counts = filtered_data.groupby(['State', 'Severity']).agg({'ID': 'count'}).reset_index()
state_severity_counts.columns = ['State', 'Severity', 'Accident_Count']

# Compute total counts for each state and percentages
state_total_counts = filtered_data.groupby('State').agg({'ID': 'count'}).reset_index()
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




fig = px.bar(
    state_severity_counts,
    y= "State",
    x = "Accident_Count",
    color='Severity',
    orientation='h',
    custom_data=["Tooltip"],  # Pass tooltip data
    hover_data={"Tooltip"},
    category_orders={"State": state_severity_counts['State'].unique(),
                     "Severity": ['Critical', 'High', 'Medium', 'Low']}
)

fig.update_layout(
    yaxis_title="State",
    xaxis_title="Accident Count",
    height = 1000,
    margin={"r": 0, "t": 50, "l": 0, "b": 50},  # Adjust margins for better fit
    legend=dict(
        yanchor="top",
        y=0.95,
        xanchor="right",
        x=0.9
    )
)


st.plotly_chart(fig, use_container_width=True)


"""
Adding Choropleth plot 
"""

state_yearly_accidents = filtered_data.groupby(['State']).agg({'ID': 'count'}).reset_index()
state_yearly_accidents.columns = ['State','Accident_Count']

# Step 4: Aggregate accident counts by severity for each state and year
state_yearly_severity_counts = filtered_data.groupby(['State', 'Severity']).agg({'ID': 'count'}).reset_index()
state_yearly_severity_counts.columns = ['State', 'Severity', 'Severity_Count']

# Step 5: Merge the total accident counts and severity counts into one DataFrame
state_yearly_data = pd.merge(state_yearly_accidents, state_yearly_severity_counts, on=['State'], how='left')
all_states = [
    "Alabama", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida",
    "Georgia", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
    "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana",
    "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina",
    "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina",
    "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
    "Wisconsin", "Wyoming"
]
all_states_df = pd.DataFrame({"State": all_states})
state_yearly_data = pd.merge(all_states_df, state_yearly_data, on="State", how="left")


# Create the tooltip column with all severity counts
def get_severity_count(state_code, severity):
    # Filter the data for the state and severity
    severity_count = state_yearly_data[(state_yearly_data['State'] == state_code) & 
                                       (state_yearly_data['Severity'] == severity)]
    
    # If the severity count exists, return it; otherwise, return 0
    if not severity_count.empty:
        return severity_count['Severity_Count'].values[0]
    else:
        return 0  # If no data, return 0

# Generate the tooltip for each row
state_yearly_data['tooltip'] = state_yearly_data.apply(
    lambda row: f"Total Accidents: {row['Accident_Count']}<br>"
                f"Low: {get_severity_count(row['State'], 'Low')}<br>"
                f"Medium: {get_severity_count(row['State'], 'Medium')}<br>"
                f"High: {get_severity_count(row['State'], 'High')}<br>"
                f"Critical: {get_severity_count(row['State'], 'Critical')}",
    axis=1)


state_yearly_data = state_yearly_data.sort_values(by=["Accident_Count"], ascending=[False])

from pandas.api.types import CategoricalDtype
severity_order = CategoricalDtype(categories=['Critical', 'High', 'Medium', 'Low'], ordered=True)

# Apply the custom category order to the Severity column
state_yearly_data['Severity'] = state_yearly_data['Severity'].astype(severity_order)


state_yearly_data = state_yearly_data[['State', 'Accident_Count', 'tooltip']].drop_duplicates()
state_yearly_data['Accident_Count'] = state_yearly_data['Accident_Count'].fillna(0)

adjusted_data = state_yearly_data.copy()
adjusted_data.loc[adjusted_data['State'] == 'California', 'Accident_Count'] = min(
    adjusted_data[adjusted_data['State'] != 'California']['Accident_Count'].max() * 1.2,
    adjusted_data.loc[adjusted_data['State'] == 'California', 'Accident_Count'].values[0]
)

geojson_file = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
geojson_data = requests.get(geojson_file).json()

m = folium.Map(location=[37.0902, -95.7129], zoom_start=4, tiles="cartodbpositron")

# Merge the DataFrame into the GeoJSON
for feature in geojson_data["features"]:
    state_name = feature["properties"]["name"]  # GeoJSON state name
    # Match state name and add Accident_Count and tooltip data
    match = state_yearly_data[state_yearly_data["State"] == state_name]
    if not match.empty:
        feature["properties"]["Accident_Count"] = int(match["Accident_Count"].iloc[0])
        feature["properties"]["tooltip"] = match["tooltip"].values[0]
    else:
        feature["properties"]["Accident_Count"] = 0
        feature["properties"]["tooltip"] = "No data available"

folium.Choropleth(
    geo_data=geojson_data,  # GeoJSON data for US states
    data = adjusted_data,  # Data containing accident counts
    columns=["State", "Accident_Count"],  # Columns to match and color by
    key_on="feature.properties.name",  # GeoJSON key to match State_Code (usually in the 'id' field)
    fill_opacity=0.7,
    line_opacity=0.2,
    fill_color="viridis",
    legend_name="Accident Count by State"
).add_to(m)


tooltip = folium.GeoJsonTooltip(
    fields=["name", "tooltip"],
    aliases=["State:", "Severity Counts:"],
    localize=True,
    sticky=True,
    labels=True,
    style="""
        background-color: #F0EFEF;
        border: 2px solid black;
        border-radius: 3px;
        box-shadow: 3px;
    """,
    max_width=800,
)


folium.GeoJson(
    geojson_data,
    tooltip=tooltip
).add_to(m)

st_folium(m, width=725)
