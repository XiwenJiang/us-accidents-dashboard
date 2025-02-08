import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from folium.features import GeoJsonTooltip
from streamlit_folium import st_folium
from constants import US_CITIES_COORDS
import plotly.express as px
import plotly.graph_objects as go
from data_processing import get_severity_data, get_county_data

box_template = """
<div style="background:{}; padding:15px; border-radius:10px; text-align:center; color:white; font-size:18px;">
    <b>{}</b><br>
    <span style="font-size:24px;">{}</span><br>
    <span style="font-size:14px;">Δ {}</span>
</div>
"""

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
                                        })
    county_bubble.update_layout(showlegend=False)
    return county_bubble

# Area chart of severity distribution over time
def area_chart_severrity():
    # Extract year and quarter from Start_Time
    data['Quarter'] = data['Start_Time'].dt.quarter
    data['YearQuarter'] = data['Year'].astype(str) + '-Q' + data['Quarter'].astype(str)

    # Group by state and time period
    severity_qt_yr_df = data.groupby(['Severity', 'YearQuarter'])['ID'].count().reset_index(name='Count')

    # create area chart
    fig = px.area(severity_qt_yr_df, x='YearQuarter', y='Count', color='Severity', 
                title='Severity Distribution Over Time',
                labels={'YearQuarter': 'Year-Quarter', 'Count': 'Number of Accidents'},
                color_discrete_sequence=colors)
    fig.update_layout(legend_title_text='Severity', legend_title_side="left")
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5))
    return fig


colors = ["#FF5733", "#FF8C00", "#FFD700", "#28A745"]  # 红，橙，黄，绿


data = st.session_state.data
severity_df = get_severity_data(data)


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
    st.plotly_chart(area_chart_severrity(), use_container_width=True)

with col3:
    # create a heatmap of los angeles with selected severity level
    select_severity = st.selectbox('Select Severity Level', ['Critical', 'High', 'Medium', 'Low'])
    severity_data = data[(data['Severity'] == select_severity) & (data['County'] == 'Los Angeles')]
    severity_data
    heat_data = [[row['Start_Lat'], row['Start_Lng']] for index, row in severity_data.iterrows()]
    from folium.plugins import HeatMap
    def create_heatmap(df_loc, latitude, longitude, zoom =12, tiles='OpenStreetMap'):
        heat_data = [[row['Start_Lat'], row['Start_Lng']] for index, row in df_loc.iterrows()]
        world_map = folium.Map(location=[latitude, longitude], zoom_start=zoom, tiles=tiles)
        HeatMap(heat_data).add_to(world_map)
        return world_map

    la_heatmap = create_heatmap(
        severity_data,
        34.0522, 
        -118.0437, # lat, lon of Los Angeles
        10 #zoom level
    )   
    st_folium(la_heatmap, width=800, height=400)