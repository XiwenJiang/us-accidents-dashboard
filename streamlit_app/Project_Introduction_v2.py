import pandas as pd
import streamlit as st

S3_BASE = "s3://us-accidents-dashboard-1445/processed"

@st.cache_data(ttl=3600)
def load_table(name: str) -> pd.DataFrame:
    return pd.read_parquet(f"{S3_BASE}/{name}/")

st.set_page_config(page_title="US Accidents Dashboard (v2)", layout="wide")
st.title("US Accidents Dashboard (v2: Parquet-only)")

df_state = load_table("state_counts")

st.subheader("Top States by Accident Count")
st.dataframe(df_state.head(15))

st.caption("Data source: S3 Parquet (processed/state_counts). No raw CSV loaded at app startup.")
