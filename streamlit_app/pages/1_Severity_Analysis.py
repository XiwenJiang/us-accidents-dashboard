from tabnanny import check
import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from folium.features import GeoJsonTooltip
from streamlit_folium import st_folium
from constants import US_CITIES_COORDS, US_STATES 
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy.stats import gaussian_kde
from data_processing import (get_state_analysis_data, 
                             get_tooltip,
                             create_heatmap,
                             get_weather_data)


box_template = """
<div style="background:{}; padding:15px; border-radius:10px; text-align:center; color:white; font-size:18px;">
    <b>{}</b><br>
    <span style="font-size:24px;">{}</span><br>
    <span style="font-size:14px;">Δ {}</span>
</div>
"""

S3_BASE = "s3://us-accidents-dashboard-1445/processed"

@st.cache_data(ttl=3600)
def load_table(name: str):
    return pd.read_parquet(f"{S3_BASE}/{name}/")

def create_severity_pie(severity_df):
    # Sort the DataFrame to ensure correct order
    severity_order = ['Critical', 'High', 'Medium', 'Low']
    severity_df = severity_df.set_index('Severity Level').reindex(severity_order).reset_index()
    
    severity_pie = px.pie(
        severity_df, 
        values='Count', 
        names='Severity Level', 
        title='Severity Distribution',
        color='Severity Level',
        category_orders={'Severity Level': severity_order},
        color_discrete_map={
            'Critical': colors[0],
            'High': colors[1],
            'Medium': colors[2],
            'Low': colors[3]
        },
        hole=0.5
    )
    
    severity_pie.update_traces(
        textposition='outside',
        textinfo='percent+label',
        pull=[0.1, 0.1, 0.1, 0.1]  # Add some space between slices
    )
    severity_pie.update_layout(
        showlegend=False,  # Remove legend
        margin=dict(t=30, l=30, r=30, b=30),  # Adjust margins
        height=300,  # Reduced height
        width=400   # Added specific width
    )
    return severity_pie
    
def top_10_state_barplot():
    df = load_table("state_yearly_summary").copy()
    # # 选择一个年份：先用最新年份（也可以后面加 selectbox）
    # latest_year = int(df["Year"].max())
    # df = df[df["Year"] == latest_year].copy()
    agg = (
        df
        .groupby("State_Code", as_index=False)
        .agg({
            "Accident_Count": "sum",
            "Critical": "sum",
            "High": "sum",
            "Medium": "sum",
            "Low": "sum"
        })
    )

    # 映射州名
    agg["State"] = agg["State_Code"].map(US_STATES)

    # Top10 states by total accidents
    top10 = (
        agg
        .sort_values("Accident_Count", ascending=False)
        .head(10)
        .copy()
    )
    


    # tooltip（每州一条）
    top10["Tooltip"] = (
        "State: " + top10["State"].astype(str) + "<br>"
        "Total: " + top10["Accident_Count"].astype(int).map(lambda x: f"{x:,}") + "<br>"
        "Critical: " + top10["Critical"].astype(int).map(lambda x: f"{x:,}") + "<br>"
        "High: " + top10["High"].astype(int).map(lambda x: f"{x:,}") + "<br>"
        "Medium: " + top10["Medium"].astype(int).map(lambda x: f"{x:,}") + "<br>"
        "Low: " + top10["Low"].astype(int).map(lambda x: f"{x:,}")
    )

    

    # 转成长表：State x Severity
    long = top10.melt(
        id_vars=["State", "Accident_Count", "Tooltip"],
        value_vars=["Critical", "High", "Medium", "Low"],
        var_name="Severity",
        value_name="Severity_Count",
    ).rename(columns={"State": "State"})

    
    state_order = top10.sort_values("Accident_Count", ascending=False)["State"].tolist()
    
    top10_bar = px.bar(
        long,
        y="State",
        x="Severity_Count",
        color="Severity",
        orientation="h",
        custom_data=["Tooltip"],
        hover_data={"Tooltip": True},
        category_orders={
            "State": state_order,
            "Severity": ["Critical", "High", "Medium", "Low"]
        },
        color_discrete_map={
            "Critical": "#FF5733",
            "High": "#FF8C00",
            "Medium": "#FFD700",
            "Low": "#28A745"
        },
        title=f"Top 10 States Accident Counts by Severity"
    )
    

    top10_bar.for_each_trace(
        lambda trace: trace.update(
            hovertemplate="%{customdata[0]}<extra></extra>"
        )
    )

    top10_bar.update_layout(
        yaxis_title="State",
        xaxis_title="Accident Count",
        barmode="stack",
        height=400,
        margin={"r": 0, "t": 50, "l": 0, "b": 50},
        legend=dict(
            yanchor="top",
            y=0.33,
            xanchor="right",
            x=0.9
        ),
    )
    return top10_bar


def color_bubble_county_count():
    county_fips = pd.read_csv('county_fips.csv')
    county_fips['STCOUNTYFP'] = county_fips['STCOUNTYFP'].astype(str).str.zfill(5)

    county_bubble = px.scatter_mapbox(county_fips,
                                    lat="lat",
                                    lon="lng",
                                    size="Count",
                                    color="State",
                                    zoom=2.8,
                                    size_max=80,
                                    title="County-level Accident Counts",
                                    mapbox_style="carto-positron",
                                    hover_name="County",
                                    hover_data={
                                        "tooltip": True,
                                        "lat": False,
                                        "lng": False
                                    },
                                    height=600)  # Increased height from default to 600
    county_bubble.update_layout(
        showlegend=False,
        margin=dict(t=30, r=10, l=10, b=10)  # Adjusted margins to maximize map space
    )
    return county_bubble
 
# Area chart of severity distribution over time
def area_chart_severity():
    severity_order = ['Critical', 'High', 'Medium', 'Low']
    severity_map = {1:"Low",2:"Medium",3:"High",4:"Critical"}

    df = load_table("state_yearquarter_severity_counts")
    df["Severity"] = df["Severity"].map(severity_map)

    severity_qt_yr_df = (
        df.groupby(["YearQuarter","Severity"], as_index=False)["Severity_Count"]
        .sum()
        .rename(columns={"Severity_Count":"Count"})
    )

    severity_qt_yr_df["Severity"] = pd.Categorical(
        severity_qt_yr_df["Severity"], categories=severity_order, ordered=True
    )

    # create area chart with explicit color mapping
    fig = px.area(
        severity_qt_yr_df, 
        x='YearQuarter', 
        y='Count', 
        color='Severity', 
        title='Severity Distribution Over Time',
        labels={'YearQuarter': 'Year-Quarter', 'Count': 'Number of Accidents'},
        category_orders={'Severity': severity_order},
        color_discrete_map={
            'Critical': colors[0],  # "#FF5733" - Red
            'High': colors[1],      # "#FF8C00" - Orange
            'Medium': colors[2],    # "#FFD700" - Yellow
            'Low': colors[3]        # "#28A745" - Green
        }
    )
    
    fig.update_layout(
        legend_title_text='Severity',
        legend_title_side="left",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )
    return fig

def create_radar_chart_from_agg(road_by_sev_df, select_severity):
    road_conditions = ['Bump','Crossing','Give_Way','Junction','Stop','No_Exit','Traffic_Signal']
    row = road_by_sev_df[road_by_sev_df["Severity"] == select_severity]
    if row.empty:
        return go.Figure()

    vals = row[road_conditions].iloc[0].tolist()

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals,
        theta=road_conditions,
        fill='toself',
        name=select_severity
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        showlegend=False,
        title=f'Road Condition by - {select_severity} Severity',
        height=400,
        width=800,
        margin=dict(t=50, l=50, r=50, b=50)
    )
    return fig
    

colors = ["#FF5733", "#FF8C00", "#FFD700", "#28A745"]  # 红，橙，黄，绿

severity_map = {1:"Low",2:"Medium",3:"High",4:"Critical"}

sev = load_table("severity_counts").rename(columns={"accident_count":"Count"})
if sev["Severity"].dtype != object:
    sev["Severity"] = sev["Severity"].map(severity_map)

sev["Percentage"] = sev["Count"] / sev["Count"].sum() * 100

severity_df = sev.rename(columns={"Severity":"Severity Level"})[["Severity Level","Count","Percentage"]]

col1, col2, col3 = st.columns((0.3, 0.4, 0.3), gap ='small')

with col2:
    # Display the severity data
    col2_1, col2_2, col2_3, col2_4 = st.columns([1, 1, 1, 1])
    with col2_1:
        st.markdown(box_template.format(colors[0], "Critical", severity_df['Count'][0], f"{severity_df['Percentage'][0]:.2f}%"), unsafe_allow_html=True)
        
    with col2_2:
        st.markdown(box_template.format(colors[1], "High", severity_df['Count'][1], f"{severity_df['Percentage'][1]:.2f}%"), unsafe_allow_html=True)
        
    with col2_3:
        st.markdown(box_template.format(colors[2], "Medium", severity_df['Count'][3], f"{severity_df['Percentage'][3]:.2f}%"), unsafe_allow_html=True)
        
    with col2_4:
        st.markdown(box_template.format(colors[3], "Low", severity_df['Count'][2], f"{severity_df['Percentage'][2]:.2f}%"), unsafe_allow_html=True)

    # Add county-level analysis
    st.plotly_chart(color_bubble_county_count(), use_container_width=True)
    st.plotly_chart(area_chart_severity(), use_container_width=True)
    

with col1:
    st.plotly_chart(create_severity_pie(severity_df), use_container_width=True)
    st.plotly_chart(top_10_state_barplot(), use_container_width=True)

    numerical_cols = ['Temperature(F)', 'Humidity(%)', 'Pressure(in)', 'Visibility(mi)', 'Wind_Speed(mph)', 'Precipitation(in)']
    
    weather_df = load_table("weather_numeric_sample").copy()

    severity_map = {1:"Low",2:"Medium",3:"High",4:"Critical"}
    if weather_df["Severity"].dtype != object:
        weather_df["Severity"] = weather_df["Severity"].map(severity_map)

    select_weather = st.selectbox('Select Weather Condition', numerical_cols)
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
        colors_ = px.colors.qualitative.Set2
        severity_order = ['Critical', 'High', 'Medium', 'Low']

        try:
            for i, sev in enumerate(severity_order):
                sev_series = data_clean[data_clean['Severity'] == sev][column].dropna()

                if len(sev_series.unique()) > 1:
                    kde = gaussian_kde(sev_series)

                    if column == 'Precipitation(in)':
                        x_range = np.linspace(0, 4, 200)
                    else:
                        x_range = np.linspace(sev_series.min(), sev_series.max(), 200)

                    fig.add_trace(
                        go.Scatter(
                            x=x_range,
                            y=kde(x_range),
                            name=sev,
                            mode='lines',
                            line=dict(width=2, color=colors_[i])
                        )
                    )

            layout_dict = {
                'title': f'Weather Condition ({column}) Impact by Severity',
                'xaxis_title': column,
                'yaxis_title': 'Density',
                'width': 800,
                'height': 400,
                'showlegend': True,
                'legend_title_text': 'Severity'
            }
            if column == 'Precipitation(in)':
                layout_dict['xaxis'] = dict(range=[0, 4])

            fig.update_layout(**layout_dict)

        except np.linalg.LinAlgError:
            st.warning(f"Could not compute KDE for {column}")
            return None

        return fig

    st.plotly_chart(create_kde_plot(weather_df, select_weather), use_container_width=True)



with col3:
    # create a heatmap of los angeles with selected severity level
    st.markdown("""
        <style>
            /* Increase font size of selectbox text */
            div[data-baseweb="select"] > div {
                font-size: 17px !important; 
            }
                
            label[data-testid="stWidgetLabel"] {
                font-size: 25px !important; /* Adjust as needed */
                font-weight: bold; /* Make it bold */
                color: red; /* Change color if needed */
            }

        </style>
    """, unsafe_allow_html=True)
    select_severity = st.selectbox('# Select Severity Level', ['Critical', 'High', 'Medium', 'Low'])
    la_points = load_table("la_points_all").copy()

    severity_map = {1:"Low",2:"Medium",3:"High",4:"Critical"}
    if la_points["Severity"].dtype != object:
        la_points["Severity"] = la_points["Severity"].map(severity_map)

    severity_data_all = la_points[la_points["Severity"] == select_severity]

    MAX_POINTS = 50000  # 推荐 20k-80k 之间
    if len(severity_data_all) > MAX_POINTS:
        severity_data = severity_data_all.sample(n=MAX_POINTS, random_state=42)
    else:
        severity_data = severity_data_all

    la_heatmap = create_heatmap(
        severity_data,
        34.0522,
        -118.0437,
        10
    )

    st.markdown(f"<h5 style='text-align: center; margin-bottom: 20px;'>Los Angeles Heat Map - {select_severity} Severity</h5>", unsafe_allow_html=True)

    # Set fixed height for both container and map
    map_container = st.container()
    with map_container:
        _map = st_folium(
            la_heatmap,
            key=f"map_{select_severity}",  # Add unique key to force refresh
            height=545,  # Increased height for better visibility
            use_container_width=True
        )
    
    road_by_sev = load_table("road_conditions_by_severity").copy()
    if road_by_sev["Severity"].dtype != object:
        road_by_sev["Severity"] = road_by_sev["Severity"].map(severity_map)


    st.plotly_chart(create_radar_chart_from_agg(road_by_sev, select_severity), use_container_width=True)

    # weather_condition_severity_df = data[data['Severity'] == select_severity].groupby('Weather_Condition').size().reset_index(name='Count').sort_values(by='Count', ascending=False)

