import pandas as pd
import streamlit as st

S3_ANALYTICS_PREFIX = "s3://us-accidents-dashboard-1445/processed"

@st.cache_data
def load_table(table_name: str) -> pd.DataFrame:
    """Load a processed table from S3 into a Pandas DataFrame."""
    path = f"{S3_ANALYTICS_PREFIX}/{table_name}/"
    return pd.read_parquet(path)

# -------------------------
# Temporal Analysis
# -------------------------

def get_temporal_data():
    """
    Replace old temporal data loading logic with new processed data.
    """
    return load_table("accidents_by_year_month")

def get_top_10_states_by_quarter():
    """Top 10 states per quarter (precomputed by Spark)."""
    return load_table("top_states_by_quarter")

def get_racing_bar_tooltip(df: pd.DataFrame) -> pd.DataFrame:
    """Keep lightweight tooltip logic here."""
    # implement your existing tooltip formatting on small df
    return df



# -------------------------
# Regional Analysis
# -------------------------
def get_state_analysis_data():
    """
    State-level summary for choropleth / tables.
    """
    # If you only need counts:
    return load_table("state_counts")

def get_state_yearly_data():
    """State x year accident counts (precomputed)."""
    return load_table("state_yearly_counts")

def get_city_statistics():
    """Top cities table (precomputed)."""
    return load_table("city_counts_topN")

def create_geojson_data(geojson_obj, df_state: pd.DataFrame):
    """
    Keep here if it is only merging geojson properties for 50 states.
    """
    # your existing merge logic here
    return geojson_obj

def get_tooltip(df: pd.DataFrame) -> pd.DataFrame:
    """Keep tooltip formatting on small df."""
    return df

# -------------------------
# Severity Analysis
# -------------------------
def get_severity_data():
    """Overall severity distribution (precomputed)."""
    return load_table("severity_counts")

def get_severity_by_hour():
    """Severity x hour distribution (already built)."""
    return load_table("severity_by_hour")

def create_heatmap(df_points: pd.DataFrame):
    """
    Heatmap should use downsampled points or aggregated grid cells.
    """
    return df_points

# -------------------------
# Weather Impact
# -------------------------
def get_weather_data():
    """Weather condition x severity counts (precomputed)."""
    return load_table("weather_severity_counts")