# app.py

import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from data_loader import get_data

# --- APP CONFIGURATION ---
# Load environment variables from .env file.
# This ensures the app can find the database connection string.
#load_dotenv()

# --- DATA LOADING ---
# Use Streamlit's cache to load data only once.
# This prevents the app from querying the database on every user interaction,
# making it fast and efficient.
@st.cache_data
def load_all_data():
    """
    Loads all data from the database using the get_data function.
    """
    df = get_data()
    return df

# Load the data before any page logic runs.
# This makes the data available to all modules.
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
page = st.sidebar.radio("Go to", ["Overview", "Basic Dashboard", "Risk Analysis", "Performance Comparison"])

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

elif page == "Performance Comparison":
    # Check if data was loaded successfully before displaying the page
    if not df_raw.empty:
        performance_comparison.show_page(df_raw)
    else:
        st.warning("Could not load data for performance comparison. Please check the database connection and data pipeline.")