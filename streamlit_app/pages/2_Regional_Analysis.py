import streamlit as st
import pandas as pd
import plotly.express as px
import folium
import requests
from streamlit_folium import st_folium
from folium.plugins import HeatMap
from constants import US_CITIES_COORDS, US_STATES
from data_processing import create_geojson_data
st.set_page_config(layout="wide")

S3_BASE = "s3://us-accidents-dashboard-1445/processed"

@st.cache_data(ttl=3600)
def load_table(name: str):
    return pd.read_parquet(f"{S3_BASE}/{name}/")

CARD_HEIGHT = 520  
PLOT_HEIGHT = 400

st.title("Location Analysis")
# st.write("""
#          In this dataset, we have different attributes like City, State, Timezone
#          and even street for each accident records. Here we will analyze these four
#          features based on the no. of cases for each distinct location.
#          """)


st.sidebar.title("Select Filters")
state_yearly = load_table("state_yearly_summary").copy()
years = sorted(state_yearly["Year"].unique().tolist())
years_label = ["2016-2023"] + [str(y) for y in years]
def normalize_year_selection(selected_years, all_years):
    """
    selected_years: list like ['2016-2023'] or ['2019','2020'] or []
    all_years: list[int] like [2016,2017,...,2023]
    returns:
      year_filter: list[int]
      year_label: str
    """
    # empty -> fallback
    if not selected_years:
        selected_years = ["2016-2023"]

    if "2016-2023" in selected_years:
        return all_years, "2016–2023"

    # selected_years are strings or ints depending on your options; normalize to int
    years_int = sorted([int(y) for y in selected_years])
    if len(years_int) == 1:
        return years_int, str(years_int[0])

    return years_int, f"{years_int[0]}–{years_int[-1]}"

all_years = sorted(state_yearly["Year"].unique().tolist())  # 或其它来源
selected_years = st.sidebar.multiselect("Select Year", years_label, default=[years_label[0]])

year_filter, year_label = normalize_year_selection(selected_years, all_years)


col1, col2 = st.columns([1,1])

# Get processed state data
df = state_yearly[state_yearly["Year"].isin(year_filter)].copy()

# 聚合多年份：总数相加
agg = (
    df.groupby("State_Code", as_index=False)[["Accident_Count","Low","Medium","High","Critical"]]
      .sum()
)

# 州名（你说你希望用 full name）
agg["State"] = agg["State_Code"].map(US_STATES)

top10 = agg.sort_values("Accident_Count", ascending=False).head(10).copy()

top10["Tooltip"] = (
    "State: " + top10["State"].astype(str) + "<br>"
    "Years: " + ("All" if "2016-2023" in selected_years else ", ".join(map(str, year_filter))) + "<br>"
    "Total: " + top10["Accident_Count"].astype(int).map(lambda x: f"{x:,}") + "<br>"
    "Critical: " + top10["Critical"].astype(int).map(lambda x: f"{x:,}") + "<br>"
    "High: " + top10["High"].astype(int).map(lambda x: f"{x:,}") + "<br>"
    "Medium: " + top10["Medium"].astype(int).map(lambda x: f"{x:,}") + "<br>"
    "Low: " + top10["Low"].astype(int).map(lambda x: f"{x:,}")
)

long = top10.melt(
    id_vars=["State","Accident_Count","Tooltip"],
    value_vars=["Critical","High","Medium","Low"],
    var_name="Severity",
    value_name="Severity_Count",
)

state_order = top10.sort_values("Accident_Count", ascending=False)["State"].tolist()

# Create state bar chart
top10_bar = px.bar(
    long,
    y="State",
    x="Severity_Count",
    color="Severity",
    orientation="h",
    custom_data=["Tooltip"],
    hover_data={"Tooltip": True},
    category_orders={"State": state_order, "Severity": ["Critical","High","Medium","Low"]},
    color_discrete_map={
        "Critical": "#FF5733",
        "High": "#FF8C00",
        "Medium": "#FFD700",
        "Low": "#28A745"
    },
)

top10_bar.for_each_trace(lambda t: t.update(hovertemplate="%{customdata[0]}<extra></extra>"))
top10_bar.update_layout(barmode="stack", height=PLOT_HEIGHT)


top10_bar.for_each_trace(
    lambda trace: trace.update(
        hovertemplate="%{customdata[0]}<extra></extra>"  # Use Tooltip column and remove default hover info
    )
)

top10_bar.update_layout(
    yaxis_title="State",
    xaxis_title="Accident Count",
    barmode="stack",
    height = 400,
    margin={"r": 0, "t": 50, "l": 0, "b": 50},  # Adjust margins for better fit
    legend=dict(
        yanchor="top",
        y=0.33,
        xanchor="right",
        x=0.9
    )
)

# Get state yearly data
state_map_df = agg[["State","Accident_Count","Low","Medium","High","Critical"]].copy()

state_map_df["tooltip"] = (
    "Total: " + state_map_df["Accident_Count"].astype(int).map(lambda x: f"{x:,}") + "<br>"
    "Critical: " + state_map_df["Critical"].astype(int).map(lambda x: f"{x:,}") + "<br>"
    "High: " + state_map_df["High"].astype(int).map(lambda x: f"{x:,}") + "<br>"
    "Medium: " + state_map_df["Medium"].astype(int).map(lambda x: f"{x:,}") + "<br>"
    "Low: " + state_map_df["Low"].astype(int).map(lambda x: f"{x:,}")
)

# Process GeoJSON data
geojson_file = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
geojson_data = requests.get(geojson_file).json()
geojson_data = create_geojson_data(state_map_df, geojson_data)

# Create map
m = folium.Map(location=[37.0902, -95.7129], zoom_start=4, tiles="cartodbpositron")

# Merge the DataFrame into the GeoJSON
for feature in geojson_data["features"]:
    state_name = feature["properties"]["name"]  # GeoJSON state name
    # Match state name and add Accident_Count and tooltip data
    match = state_map_df[state_map_df["State"] == state_name]

    if not match.empty:
        feature["properties"]["Accident_Count"] = int(match["Accident_Count"].iloc[0])
        feature["properties"]["tooltip"] = match["tooltip"].values[0]
    else:
        feature["properties"]["Accident_Count"] = 0
        feature["properties"]["tooltip"] = "No data available"

folium.Choropleth(
    geo_data=geojson_data,  # GeoJSON data for US states
    data=state_map_df,  # Changed from adjusted_data to state_map_df
    columns=["State", "Accident_Count"],
    key_on="feature.properties.name",
    fill_opacity=0.7,
    line_opacity=0.2,
    fill_color="viridis",
    legend_name="Accident Count by State"
).add_to(m)


tooltip = folium.GeoJsonTooltip(
    fields=["name", "tooltip"],
    aliases=["State:", "Severity:"],
    localize=True,
    sticky=True,
    labels=False,
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

with col1:
    with st.container(height=CARD_HEIGHT):
        st.markdown(f"#### Top 10 State With Severity in {year_label}")
        st.plotly_chart(top10_bar, use_container_width=True)

    with st.container(height=CARD_HEIGHT):
        st.markdown(f"#### Accident Location by State in {year_label}")
        st_folium(m, use_container_width=True, height=PLOT_HEIGHT, returned_objects=[])



# Process city data
city_year_df = load_table("city_year_counts_top200").copy()

# 1) 年份过滤
city_year_df = city_year_df[city_year_df["Year"].isin(year_filter)]

# 2) 如果选了多个年份，把它们合并成一个总排名（与你州级 agg 的逻辑一致）
city_rank = (
    city_year_df.groupby("City", as_index=False)["Accident_Count"]
               .sum()
               .sort_values("Accident_Count", ascending=False)
)

top_10_cities = city_rank.head(10).copy()
top_10_cities["Percentage"] = top_10_cities["Accident_Count"] / top_10_cities["Accident_Count"].sum() * 100

# Create the bar plot
top_10_city_bar = px.bar(
    top_10_cities,
    x="City",
    y="Accident_Count",
    text=top_10_cities["Percentage"].apply(lambda x: f"{x:.2f}%"),  # Add percentage as text
    # title="'\nTop 10 Cities in US with most no. of \nRoad Accident Cases (2016-2020)\n'",
    labels={"Accident_Count": "Accident Count", "City": "City"},
    color="City" # Use Rainbow color sequence
)

# Customize the layout
top_10_city_bar.update_traces(
    textposition="inside",  # Place the percentage text inside the bars
    textfont=dict(
        size=12,  # Font size
        color="white",  # White text
        family="Arial"  # Font family
        # Removed the weight property as it's not supported
    ),   
    hovertemplate="City: %{x}<br>Accident Count: %{y}<br>Percentage: %{text}<extra></extra>"
)

top_10_city_bar.update_layout(
    xaxis_title="City",
    yaxis_title="Accident Count",
    margin=dict(l=50, r=50, t=50, b=50),
    coloraxis_colorbar=dict(
        title="Accident Count"
    ),
    height = PLOT_HEIGHT
)




with col2:
    with st.container(height=CARD_HEIGHT):
        st.markdown(f"#### Top 10 Cities in US with most no. of Road Accident Cases in {year_label}")
        st.plotly_chart(top_10_city_bar, use_container_width=True)

    with st.container(height=CARD_HEIGHT):

        city_options = city_rank.head(200)["City"].tolist()
        selected_city = st.selectbox(
            "Select a city to display heatmap:", 
            options=city_options, 
            index=0)


        # Filter the data for the selected city
        city_points = load_table("city_points_year_sample")

        # 年份过滤 + 城市过滤
        pts = city_points[city_points["Year"].isin(year_filter)]
        pts = pts[pts["City"] == selected_city][["Start_Lat", "Start_Lng"]]

        # 这里可以加一个安全阈值，防止某些城市点数太多拖慢 folium
        MAX_POINTS = 50000
        if len(pts) > MAX_POINTS:
            pts = pts.sample(n=MAX_POINTS, random_state=42)

        filtered_cities = pts

        heat_data = [[row['Start_Lat'], row['Start_Lng']] for index, row in filtered_cities.iterrows()]
        def create_heatmap(df_loc, latitude, longitude, zoom =12, tiles='OpenStreetMap'):
            """
            Generate a Folium Map with a heatmap of accident locations.
            """
            # Create a list of coordinates from the dataframe columns 'Start_Lat' and 'Start_Lng'
            heat_data = [[row['Start_Lat'], row['Start_Lng']] for index, row in df_loc.iterrows()]

            # Create a map centered around the specified coordinates
            world_map = folium.Map(location=[latitude, longitude], zoom_start=zoom, tiles=tiles)

            # Add the heatmap layer to the map
            HeatMap(heat_data).add_to(world_map)

            return world_map

        map_us_heatmap = create_heatmap(
            filtered_cities, 
            US_CITIES_COORDS[selected_city]['lat'],
            US_CITIES_COORDS[selected_city]['lon'], 11
        )


        st.markdown(f"#### Heatmap of Accidents in {selected_city}")
        st_folium(map_us_heatmap, width=800, height=300)

st.subheader("Insights:")
st.write("""
         1. In US, :blue[California] is the state :blue[with highest no. of road accidents] in past 5 years.
         2. About :blue[30%] of the total accident records of past 5 years in US is only from :blue[California].
         3. Florida is the 2nd highest (10% cases) state for no. road accidents in US.
         4. :blue[Miami] is the city with :blue[highest (2.42%)] no. of road accidents in US (2016-2020).
         5. Around :blue[14%] accident records of past 5 years are only from these :blue[10 cities] out of 10,657 cities in US (as per the dataset).
         """)