import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.title("Time Analysis")
st.write("Analyze accident trends over time.")
st.write("This page will feature visualizations for time-based trends.")

data = st.session_state.data


# Define the desired order for severity levels
severity_order = ['Critical', 'High', 'Medium', 'Low']

# Convert the 'Severity' column to a categorical type with the specified order
data['Severity'] = pd.Categorical(data['Severity'], categories=severity_order, ordered=True)

# Ensure 'Start_Time' is in datetime format
data['Start_Time'] = pd.to_datetime(data['Start_Time'], errors='coerce')

# Extract year from 'Start_Time'
data['Year'] = data['Start_Time'].dt.year

# Group by year and severity, and count the number of accidents
accidents_per_year_severity = data.groupby(['Year', 'Severity']).size().reset_index(name='Count')

# Plotting the data using Plotly
yr_svrt_fig = px.bar(accidents_per_year_severity, x='Year', y='Count', color='Severity', 
             title='Number of Accidents per Year by Severity',
             labels={'Year': 'Year', 'Count': 'Number of Accidents', 'Severity': 'Severity'},
             category_orders={'Severity': severity_order},
             barmode='group')

# Group by year to get the total number of accidents per year
accidents_per_year = data.groupby('Year').size().reset_index(name='Total_Count')

# Add a line chart on top of the bar chart
yr_svrt_fig.add_trace(go.Scatter(x=accidents_per_year['Year'], 
                         y=accidents_per_year['Total_Count'],
                         mode='lines+markers', 
                         name='Total Accidents', 
                         line=dict(color='green', dash = 'dashdot', width = 2)
                         ))


# Display the plot in Streamlit
st.plotly_chart(yr_svrt_fig)


col1, col2 = st.columns(2)

with col1:
    accidents_per_weekday = data.groupby('Day of Week').size().reset_index(name = 'Total_Count')

    dayofweek = {
        0: 'Monday',
        1: 'Tuesday', 
        2: 'Wednesday',
        3: 'Thursday',
        4: 'Friday',
        5: 'Saturday',
        6: 'Sunday'
    }
    accidents_per_weekday['Day of Week'] = accidents_per_weekday['Day of Week'].map(dayofweek)
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    wkdy_barfig = px.bar(accidents_per_weekday,
                        x = 'Day of Week',
                        y = 'Total_Count',
                        color= 'Day of Week',
                        category_orders={'Day of Week': weekday_order},
                        title='Accidents by Day of Week',
                        labels={'Day of Week': 'Day of Week', 'Total_Count': 'Number of Accidents'})
    wkdy_barfig.update_layout(showlegend=False)
    st.plotly_chart(wkdy_barfig)

with col2:
    accidents_per_hr = data.groupby('Hour').size().reset_index(name = "Total_Count")
    accidents_per_hr