import os
import atexit
import gdown
import streamlit as st
import plotly.express as px
import pandas as pd

# Create temp directory if it doesn't exist
TEMP_DIR = "temp"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# Initialize session state for data path
if "data_path" not in st.session_state:
    st.session_state.data_path = os.path.join(TEMP_DIR, "US_Accidents_March23_sampled_500k.csv")

def download_file_from_google_drive():
    try:
        url = "https://drive.google.com/file/d/1ZiYhNqrBPdDPndaOpJcHbXghC8052CK5/view?usp=sharing"
        file_id = url.split('/')[-2]
        direct_url = f'https://drive.google.com/uc?id={file_id}'
        
        if not os.path.exists(st.session_state.data_path):
            gdown.download(direct_url, st.session_state.data_path, quiet=False)
        
        return st.session_state.data_path
    except Exception as e:
        st.error(f"Error downloading file: {str(e)}")
        return None

def cleanup():
    if os.path.exists(st.session_state.data_path):
        os.remove(st.session_state.data_path)
    if os.path.exists(TEMP_DIR):
        os.rmdir(TEMP_DIR)

atexit.register(cleanup)

@st.cache_data
def load_data():
    # Check if data is already in session state
    if 'data' not in st.session_state:
        # Download and load data
        file_path = download_file_from_google_drive()
        data = pd.read_csv(file_path)
        
        # Store in session state
        st.session_state.data = data
    
    return st.session_state.data

st.set_page_config(layout="wide")

us_states = {'AK': 'Alaska',
 'AL': 'Alabama',
 'AR': 'Arkansas',
 'AS': 'American Samoa',
 'AZ': 'Arizona',
 'CA': 'California',
 'CO': 'Colorado',
 'CT': 'Connecticut',
 'DC': 'District of Columbia',
 'DE': 'Delaware',
 'FL': 'Florida',
 'GA': 'Georgia',
 'GU': 'Guam',
 'HI': 'Hawaii',
 'IA': 'Iowa',
 'ID': 'Idaho',
 'IL': 'Illinois',
 'IN': 'Indiana',
 'KS': 'Kansas',
 'KY': 'Kentucky',
 'LA': 'Louisiana',
 'MA': 'Massachusetts',
 'MD': 'Maryland',
 'ME': 'Maine',
 'MI': 'Michigan',
 'MN': 'Minnesota',
 'MO': 'Missouri',
 'MP': 'Northern Mariana Islands',
 'MS': 'Mississippi',
 'MT': 'Montana',
 'NC': 'North Carolina',
 'ND': 'North Dakota',
 'NE': 'Nebraska',
 'NH': 'New Hampshire',
 'NJ': 'New Jersey',
 'NM': 'New Mexico',
 'NV': 'Nevada',
 'NY': 'New York',
 'OH': 'Ohio',
 'OK': 'Oklahoma',
 'OR': 'Oregon',
 'PA': 'Pennsylvania',
 'PR': 'Puerto Rico',
 'RI': 'Rhode Island',
 'SC': 'South Carolina',
 'SD': 'South Dakota',
 'TN': 'Tennessee',
 'TX': 'Texas',
 'UT': 'Utah',
 'VA': 'Virginia',
 'VI': 'Virgin Islands',
 'VT': 'Vermont',
 'WA': 'Washington',
 'WI': 'Wisconsin',
 'WV': 'West Virginia',
 'WY': 'Wyoming'}

state_coordinates = {
    "AL": [32.806671, -86.791130],  # Alabama
    "AK": [61.370716, -152.404419],  # Alaska
    "AZ": [33.729759, -111.431221],  # Arizona
    "AR": [34.969704, -92.373123],  # Arkansas
    "CA": [36.116203, -119.681564],  # California
    "CO": [39.059811, -105.311104],  # Colorado
    "CT": [41.597782, -72.755371],  # Connecticut
    "DE": [38.989620, -75.505783],  # Delaware
    "FL": [27.766279, -81.686783],  # Florida
    "GA": [33.040619, -83.643074],  # Georgia
    "HI": [21.094318, -157.498337],  # Hawaii
    "ID": [44.240459, -114.478828],  # Idaho
    "IL": [40.349457, -88.986137],  # Illinois
    "IN": [39.849426, -86.258278],  # Indiana
    "IA": [42.011539, -93.210526],  # Iowa
    "KS": [38.526600, -96.726486],  # Kansas
    "KY": [37.668140, -84.670067],  # Kentucky
    "LA": [31.169546, -91.867805],  # Louisiana
    "ME": [44.693947, -69.381927],  # Maine
    "MD": [39.063946, -76.802101],  # Maryland
    "MA": [42.230171, -71.530106],  # Massachusetts
    "MI": [43.326618, -84.536095],  # Michigan
    "MN": [45.694454, -93.900192],  # Minnesota
    "MS": [32.741646, -89.678696],  # Mississippi
    "MO": [38.456085, -92.288368],  # Missouri
    "MT": [46.921925, -110.454353],  # Montana
    "NE": [41.125370, -98.268082],  # Nebraska
    "NV": [38.313515, -117.055374],  # Nevada
    "NH": [43.452492, -71.563896],  # New Hampshire
    "NJ": [40.298904, -74.521011],  # New Jersey
    "NM": [34.840515, -106.248482],  # New Mexico
    "NY": [42.165726, -74.948051],  # New York
    "NC": [35.630066, -79.806419],  # North Carolina
    "ND": [47.528912, -99.784012],  # North Dakota
    "OH": [40.388783, -82.764915],  # Ohio
    "OK": [35.565342, -96.928917],  # Oklahoma
    "OR": [44.572021, -122.070938],  # Oregon
    "PA": [40.590752, -77.209755],  # Pennsylvania
    "RI": [41.680893, -71.511780],  # Rhode Island
    "SC": [33.856892, -80.945007],  # South Carolina
    "SD": [44.299782, -99.438828],  # South Dakota
    "TN": [35.747845, -86.692345],  # Tennessee
    "TX": [31.054487, -97.563461],  # Texas
    "UT": [40.150032, -111.862434],  # Utah
    "VT": [44.045876, -72.710686],  # Vermont
    "VA": [37.769337, -78.169968],  # Virginia
    "WA": [47.400902, -121.490494],  # Washington
    "WV": [38.491226, -80.954456],  # West Virginia
    "WI": [44.268543, -89.616508],  # Wisconsin
    "WY": [42.755966, -107.302490],  # Wyoming
    "DC": [38.897438, -77.026817],  # Washington, D.C.
}


def state_code(state_code): return us_states[state_code]

# Load dataset
@st.cache_data
def load_data():
    # Download file if not exists
    file_path = download_file_from_google_drive()
    
    # Load and process data
    data = pd.read_csv(file_path)
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
    # Intergrate datetime columns
    data['Start_Time'] = pd.to_datetime(data['Start_Time'].str.replace(r'\.\d+$', '', regex=True), errors='coerce')
    data['End_Time'] = pd.to_datetime(data['End_Time'].str.replace(r'\.\d+$', '', regex=True), errors='coerce')
    data['Year'] = data['Start_Time'].dt.year
    data['Month'] = data['Start_Time'].dt.month
    data['Day of Week'] = data['Start_Time'].dt.dayofweek
    data['Hour'] = data['Start_Time'].dt.hour

    # Severity Levels
    severity_level = {1: 'Low', 2: 'Medium', 3: 'High', 4: 'Critical'}
    data['Severity'] = data['Severity'].map(severity_level)

    # State Code
    data['State_Code'] = data['State']
    data['State'] = data['State_Code'].apply(state_code)

    return data

st.session_state.data = load_data()



st.title("Welcome to the US Accidents Dashboard!")
data = st.session_state.data

st.subheader("Project Description")
st.write("""
    This project focuses on conducting an in-depth visual analysis of traffic accidents to identify accident hotspots, 
    examine casualty trends, uncover patterns, and derive cause-and-effect relationships. The study leverages a 
    large-scale dataset containing approximately 3.5 million traffic accident records across the contiguous United 
    States over the past five years. Each record includes a wide range of attributes, such as location, time, weather 
    conditions, natural language descriptions, points-of-interest, and other contextual factors.
# """)

# seperate page into 2 column, left column is project description, and right column is map
col2, col1= st.columns([1, 1.2])

state_yearly_accidents = data.groupby(['State_Code', 'Year']).agg({'ID': 'count'}).reset_index()
state_yearly_accidents.columns = ['State_Code', 'Year', 'Accident_Count']

# Step 4: Aggregate accident counts by severity for each state and year
state_yearly_severity_counts = data.groupby(['State_Code', 'Year', 'Severity']).agg({'ID': 'count'}).reset_index()
state_yearly_severity_counts.columns = ['State_Code', 'Year', 'Severity', 'Severity_Count']

# Step 5: Merge the total accident counts and severity counts into one DataFrame
state_yearly_data = pd.merge(state_yearly_accidents, state_yearly_severity_counts, on=['State_Code', 'Year'], how='left')


# Map state codes to lat/lon
state_yearly_data['Latitude'] = state_yearly_data['State_Code'].map(lambda x: state_coordinates[x][0])
state_yearly_data['Longitude'] = state_yearly_data['State_Code'].map(lambda x: state_coordinates[x][1])

# Step 6: Create the tooltip column with all severity counts
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



# Create the scatter_mapbox figure
fig = px.scatter_mapbox(
    state_yearly_data,
    lat="Latitude",
    lon="Longitude",
    color="Accident_Count",
    size="Accident_Count",
    hover_name="State_Code",
    hover_data={
        "tooltip": True,  # Tooltip column
        "Latitude": False,  # Hide raw latitude in hover
        "Longitude": False,  # Hide raw longitude in hover
    },
    animation_frame="Year",
    color_continuous_scale="Plasma",
    size_max=80,
    title="Accident Locations by State on the Map",
)

# Update mapbox style and layout
fig.update_layout(
    coloraxis_colorbar=dict(
        orientation="h",  # Horizontal color bar
        yanchor="bottom",  # Align to bottom
        y=-0.15,            # Move below the map
        xanchor="center",  # Center horizontally
        x=0.5,             # Center position
        title="Accident Count",  # Title for the color scale
    ),
    mapbox_style="carto-positron",  # Map style
    mapbox_zoom=3,
    mapbox_center={"lat": 37.0902, "lon": -95.7129},  # Centered on the USA
    margin={"r": 0, "t": 50, "l": 0, "b": 0},  # Remove extra margins
    height=600,  # Increase the height
    width=1000  # Increase the width

)

with col1:
    # Display the map in Streamlit
    st.plotly_chart(fig, use_container_width=True)


with col2:
    st.subheader("Study Goals")
    st.write("""
        The primary objective of this study is to raise awareness about traffic safety and highlight the importance of 
        preventive measures. Using intuitive and interactive visualizations, I aim to shed light on accident trends, 
        identify the underlying causes, and evaluate the impact of traffic-calming measures. By showcasing these insights, 
        my goal is to propose actionable solutions to improve public safety, optimize transportation systems, and ultimately 
        reduce the frequency and severity of traffic accidents.
    """)

    st.subheader("Research Questions:")
    st.write("""
        In order to accomplish my goal from this study, I am attempting to answer the folowing questions:         
        1. What are the top 10 states with highest number of traffic accidents?       
        2. Why the number of traffic accidents is high in those states?       
        3. How does the severity level differ in those states?
        4. Where the most traffic accidents happen in different geographic levels (Region, State, City, Airport code, and Zipcode)? 
        5. What is the impact of weather conditions on the number of traffic accidents?
        6. What is the impact of traffic calming, traffic signal, traffic bump, and traffic loop on the number of accidents?
        7. What effect do different time scales have on traffic accidents?
    """)
