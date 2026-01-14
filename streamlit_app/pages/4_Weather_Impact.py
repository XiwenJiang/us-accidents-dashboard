import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy.stats import gaussian_kde


# Get data and weather columns
S3_BASE = "s3://us-accidents-dashboard-1445/processed"

severity_map = {
    1: "Low",
    2: "Medium",
    3: "High",
    4: "Critical"
}

@st.cache_data(ttl=3600)
def load_table(name: str):
    return pd.read_parquet(f"{S3_BASE}/{name}/")

weather = load_table("weather_kde_sample")
weather["Severity"] = weather["Severity"].map(severity_map) 


# Filter data for top conditions and create severity distribution
weather_severity = load_table("weather_severity_counts").rename(columns={"accident_count": "Count"})
weather_severity["Severity"] = weather_severity["Severity"].map(severity_map)

# Calculate total accidents per weather condition and overall percentage
total_accidents = (
    weather_severity.groupby("Weather_Condition", as_index=False)["Count"]
    .sum()
    .sort_values("Count", ascending=False)
)
total_all = total_accidents["Count"].sum()
total_accidents["Percentage"] = (total_accidents["Count"] / total_all * 100).round(1)


top_conditions = total_accidents.head(15)["Weather_Condition"].tolist()

st.title("Weather Impact Analysis")
st.write("Analysis of how weather conditions affect accident frequency and severity.")

# Create stacked bar plot with ordered categories
weather_fig = px.bar(weather_severity,
                    x='Weather_Condition',
                    y='Count',
                    color='Severity',
                    title='Top 10 Weather Conditions by Severity',
                    category_orders={
                        'Severity': ['Critical', 'High', 'Medium', 'Low'],
                        'Weather_Condition': top_conditions  # This sets the order
                    },
                    color_discrete_sequence=px.colors.qualitative.Set2)

# Add percentage text on top of each stacked bar
for weather_type in top_conditions:
    total_pct = total_accidents[total_accidents['Weather_Condition'] == weather_type]['Percentage'].iloc[0]
    weather_fig.add_annotation(
        x=weather_type,
        y=total_accidents[total_accidents['Weather_Condition'] == weather_type]['Count'].iloc[0],
        text=f'{total_pct}%',
        showarrow=False,
        yshift=10,
        font=dict(size=14, color='black') 
    )

# Update layout
weather_fig.update_layout(
    xaxis_title='Weather Condition',
    yaxis_title='Number of Accidents',
    xaxis_tickangle=45,
    showlegend=True,
    height=600,
    width=1000,
    legend_title_text='Severity'
)

st.plotly_chart(weather_fig, use_container_width=True)


# Create KDE plots for each weather condition
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
        for i, severity in enumerate(severity_order):
            if severity not in data_clean["Severity"].unique():
                continue
            severity_data = data_clean[data_clean['Severity'] == severity][column].dropna()

            MAX_KDE_POINTS = 2000
            if len(severity_data) > MAX_KDE_POINTS:
                severity_data = severity_data.sample(MAX_KDE_POINTS, random_state=42)
            
            if len(severity_data.unique()) > 1:
                kde = gaussian_kde(severity_data)
                
                # Set different x_range for specific columns
                if column == 'Precipitation(in)':
                    x_range = np.linspace(0, 4, 200)
                else:
                    x_range = np.linspace(severity_data.min(), severity_data.max(), 200)
                
                fig.add_trace(
                    go.Scatter(
                        x=x_range,
                        y=kde(x_range),
                        name=severity,
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
        
        if column == 'Precipitation(in)':
            layout_dict['xaxis'] = dict(range=[0, 4])
        
        fig.update_layout(**layout_dict)

    except np.linalg.LinAlgError:
        st.warning(f"Could not compute KDE for {column}")
        return None
    
    return fig

# Add "All" option to weather conditions list
all_option = ["All Conditions"]
condition_options = all_option + top_conditions

selected_conditions = st.multiselect(
    "Select Weather Conditions",
    options=condition_options,
    default=top_conditions[:5],  
    key="weather_select"
)

if selected_conditions:
    if "All Conditions" in selected_conditions:
        weather_filtered = weather
    else:
        weather_filtered = weather[weather["Weather_Condition"].isin(selected_conditions)]

    col1, col2, col3 = st.columns(3)

    temp_fig = create_kde_plot(weather_filtered, "Temperature(F)")
    humid_fig = create_kde_plot(weather_filtered, "Humidity(%)")
    col1.plotly_chart(temp_fig, use_container_width=True)
    col1.plotly_chart(humid_fig, use_container_width=True)

    vis_fig = create_kde_plot(weather_filtered, "Visibility(mi)")
    precip_fig = create_kde_plot(weather_filtered, "Precipitation(in)")
    col2.plotly_chart(vis_fig, use_container_width=True)
    col2.plotly_chart(precip_fig, use_container_width=True)

    press_fig = create_kde_plot(weather_filtered, "Pressure(in)")
    wind_fig = create_kde_plot(weather_filtered, "Wind_Speed(mph)")
    col3.plotly_chart(press_fig, use_container_width=True)
    col3.plotly_chart(wind_fig, use_container_width=True)
else:
    st.warning("Please select at least one weather condition")
