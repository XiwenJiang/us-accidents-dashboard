import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy.stats import gaussian_kde

st.title("Weather Impact Analysis")
st.write("Analysis of how weather conditions affect accident frequency and severity.")

# Get data from session state
data = st.session_state.data
weather_columns = ['Temperature(F)', 'Humidity(%)', 'Pressure(in)', 'Visibility(mi)', 'Wind_Direction', 'Wind_Speed(mph)', 'Precipitation(in)', 'Weather_Condition']
road_conditions = ['Bump', 'Crossing', 'Give_Way', 'Junction', 'Stop', 'No_Exit', 'Traffic_Signal', 'Turning_Loop']
weather = data[weather_columns + road_conditions]
weather['Severity'] = data['Severity']
# Count missing values per row for weather columns
missing_per_row = weather[weather_columns].isna().sum(axis=1)

# Update weather DataFrame
weather = weather[missing_per_row < 6]

# Identify numerical columns (excluding road conditions which are binary)
numerical_cols = ['Temperature(F)', 'Humidity(%)', 'Pressure(in)', 'Visibility(mi)', 'Wind_Speed(mph)', 'Precipitation(in)']

def remove_outliers(df, column):
    q25 = df[column].quantile(0.25)
    q75 = df[column].quantile(0.75)
    iqr = q75 - q25
    lower = q25 - 1.5 * iqr
    upper = q75 + 1.5 * iqr
    return df[(df[column] >= lower) & (df[column] <= upper)]

def create_kde_plot(data, column):
    # Skip outlier removal for Visibility and Precipitation
    if column not in ['Visibility(mi)', 'Precipitation(in)']:
        data_clean = remove_outliers(data, column)
    else:
        data_clean = data
    
    fig = go.Figure()
    colors = px.colors.qualitative.Set2
    severity_order = ['Critical', 'High', 'Medium', 'Low']
    
    try:
        for i, severity in enumerate(sorted(data_clean['Severity'].unique())):
            severity_data = data_clean[data_clean['Severity'] == severity][column].dropna()
            
            if len(severity_data.unique()) > 1:
                kde = gaussian_kde(severity_data)
                
                # Set different x_range for specific columns
                if column == 'Visibility(mi)':
                    x_range = np.linspace(0, 20, 200)
                elif column == 'Precipitation(in)':
                    x_range = np.linspace(0, 4, 200)
                else:
                    x_range = np.linspace(severity_data.min(), severity_data.max(), 200)
                
                fig.add_trace(
                    go.Scatter(
                        x=x_range,
                        y=kde(x_range),
                        name=severity_order[i],
                        mode='lines',
                        line=dict(width=2, color=colors[i])
                    )
                )
        
        # Update layout with custom x-axis range
        layout_dict = {
            'title': f'Distribution of {column} by Severity',
            'xaxis_title': column,
            'yaxis_title': 'Density',
            'width': 800,
            'height': 400,
            'showlegend': True,
            'template': 'seaborn',
            'legend_title_text': 'Severity'
        }
        
        if column == 'Visibility(mi)':
            layout_dict['xaxis'] = dict(range=[0, 20])
        elif column == 'Precipitation(in)':
            layout_dict['xaxis'] = dict(range=[0, 4])
        
        fig.update_layout(**layout_dict)

    except np.linalg.LinAlgError:
        st.warning(f"Could not compute KDE for {column}")
        return None
    
    return fig

# Create and display KDE plots for all numerical columns
for col in numerical_cols:
    fig = create_kde_plot(weather, col)
    st.plotly_chart(fig)
