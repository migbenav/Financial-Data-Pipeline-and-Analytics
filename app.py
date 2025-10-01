# app.py

import streamlit as st
import pandas as pd
from data_loader import get_data # This import is correct and sufficient

# --- DATA LOADING ---
# Use Streamlit's cache to load data. 
# Set 'ttl' to 86400 seconds, which is 24 hours (60 * 60 * 24).
# This ensures the database is queried only once per day per app run, 
# improving performance and reducing API calls to Supabase.
@st.cache_data(ttl=86400) 

def load_all_data():
    """
    Loads all data from the database using the get_data function.
    This function will only re-run after 24 hours have passed since the last run.
    """
    df = get_data() 
    return df

# Load the data before any page logic runs.
df_raw = load_all_data()


# --- PAGE SETUP ---
st.set_page_config(layout="wide", page_title="Financial Data Dashboard")
st.sidebar.title("Navigation")

# Import the dashboard modules
# Assuming these files are located in a 'modules' directory
import modules.overview as overview
import modules.basic_dashboard as basic_dashboard
import modules.risk_analysis as risk_analysis
import modules.performance_comparison as performance_comparison

# Create a radio menu for page navigation
page = st.sidebar.radio("Go to", [
    "Overview", 
    "Basic Dashboard", 
    "Risk Analysis", 
    "Asset Comparison"  
])


# --- CACHE CONTROL (Manual Data Refresh Button) ---
st.sidebar.markdown("---")
st.sidebar.header("Data Control")

# Button to manually force data refresh, overriding the 24-hour cache.
if st.sidebar.button("Force Data Refresh 🔄"):
    # 1. Clear the cache for the specific data loading function
    load_all_data.clear() 
    
    # 2. Force a script re-run to load the fresh data from Supabase
    st.rerun() 
    st.sidebar.success("Data successfully refreshed!")


# --- PAGE LOGIC ---
# Display the selected page based on user input
if page == "Overview":
    overview.show_page()

elif page == "Basic Dashboard":
    # Check if data was loaded successfully before displaying the page
    if not df_raw.empty:
        basic_dashboard.show_page(df_raw)
    else:
        st.warning("Could not load data for the dashboard. Please check the database connection and data pipeline.")

elif page == "Risk Analysis":
    # Check if data was loaded successfully before displaying the page
    if not df_raw.empty:
        risk_analysis.show_page(df_raw)
    else:
        st.warning("Could not load data for risk analysis. Please check the database connection and data pipeline.")

elif page == "Asset Comparison":
    # Check if data was loaded successfully before displaying the page
    if not df_raw.empty:
        performance_comparison.show_page(df_raw)
    else:
        st.warning("Could not load data for asset comparison. Please check the database connection and data pipeline.")
