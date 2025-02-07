# State code to full name mapping
US_STATES = {'AK': 'Alaska',
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

us_states = US_STATES


# State coordinates for mapping
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
STATE_COORDINATES = state_coordinates

# City coordinates
us_cities_coords = {
    "Miami": {"lat": 25.7617, "lon": -80.1918},
    "Houston": {"lat": 29.7604, "lon": -95.3698},
    "Los Angeles": {"lat": 34.0522, "lon": -118.2437},
    "Charlotte": {"lat": 35.2271, "lon": -80.8431},
    "Dallas": {"lat": 32.7767, "lon": -96.7970},
    "Orlando": {"lat": 28.5383, "lon": -81.3792},
    "Austin": {"lat": 30.2672, "lon": -97.7431},
    "Raleigh": {"lat": 35.7796, "lon": -78.6382},
    "Nashville": {"lat": 36.1627, "lon": -86.7816},
    "Baton Rouge": {"lat": 30.4515, "lon": -91.1871},
    "Atlanta": {"lat": 33.7490, "lon": -84.3880},
    "Sacramento": {"lat": 38.5816, "lon": -121.4944},
    "San Diego": {"lat": 32.7157, "lon": -117.1611},
    "Phoenix": {"lat": 33.4484, "lon": -112.0740},
    "Minneapolis": {"lat": 44.9778, "lon": -93.2650},
    "Richmond": {"lat": 37.5407, "lon": -77.4360},
    "Oklahoma City": {"lat": 35.4676, "lon": -97.5164},
    "Jacksonville": {"lat": 30.3322, "lon": -81.6557},
    "Tucson": {"lat": 32.2226, "lon": -110.9747},
    "Columbia": {"lat": 34.0007, "lon": -81.0348},
    "Greenville": {"lat": 34.8526, "lon": -82.3940},
    "San Antonio": {"lat": 29.4241, "lon": -98.4936},
    "Saint Paul": {"lat": 44.9537, "lon": -93.0900},
    "Seattle": {"lat": 47.6062, "lon": -122.3321},
    "Portland": {"lat": 45.5051, "lon": -122.6750},
    "San Jose": {"lat": 37.3382, "lon": -121.8863},
    "Indianapolis": {"lat": 39.7684, "lon": -86.1581},
    "Denver": {"lat": 39.7392, "lon": -104.9903},
    "Chicago": {"lat": 41.8781, "lon": -87.6298},
    "Tampa": {"lat": 27.9506, "lon": -82.4572},
    "Kansas City": {"lat": 39.0997, "lon": -94.5786},
    "Tulsa": {"lat": 36.1540, "lon": -95.9928},
    "Bronx": {"lat": 40.8448, "lon": -73.8648},
    "New Orleans": {"lat": 29.9511, "lon": -90.0715},
    "Rochester": {"lat": 43.1566, "lon": -77.6088},
    "Riverside": {"lat": 33.9806, "lon": -117.3755},
    "Fort Lauderdale": {"lat": 26.1224, "lon": -80.1373},
    "Detroit": {"lat": 42.3314, "lon": -83.0458},
    "Grand Rapids": {"lat": 42.9634, "lon": -85.6681},
    "Dayton": {"lat": 39.7589, "lon": -84.1916},
    "Oakland": {"lat": 37.8044, "lon": -122.2712},
    "Columbus": {"lat": 39.9612, "lon": -82.9988},
    "Bakersfield": {"lat": 35.3733, "lon": -119.0187},
    "New York": {"lat": 40.7128, "lon": -74.0060},
    "Brooklyn": {"lat": 40.6782, "lon": -73.9442},
    "San Bernardino": {"lat": 34.1083, "lon": -117.2898},
    "Omaha": {"lat": 41.2565, "lon": -95.9345},
    "Corona": {"lat": 33.8753, "lon": -117.5664},
    "Anaheim": {"lat": 33.8366, "lon": -117.9143},
    "Long Beach": {"lat": 33.7701, "lon": -118.1937}
}
US_CITIES_COORDS = us_cities_coords


all_states = [
    "Alabama", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida",
    "Georgia", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
    "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana",
    "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina",
    "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina",
    "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
    "Wisconsin", "Wyoming"
]

ALL_STATES = all_states