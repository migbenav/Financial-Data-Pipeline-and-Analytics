# app.py
import streamlit as st
import modules.overview as overview
import modules.basic_dashboard as basic_dashboard
import modules.risk_analysis as risk_analysis
from database_utils import get_data # Asumimos que este archivo sigue en la raíz

st.set_page_config(layout="wide")
st.sidebar.title("Navigation")

# Crea un menú de radio en la barra lateral
page = st.sidebar.radio("Go to", ["Overview", "Basic Dashboard", "Risk Analysis"])

df_raw = get_data()

# Lógica para mostrar la página seleccionada
if page == "Overview":
    overview.show_page()
elif page == "Basic Dashboard":
    if not df_raw.empty:
        basic_dashboard.show_page(df_raw)
    else:
        st.warning("Could not load data for analysis. Please check the database connection.")
elif page == "Risk Analysis":
    if not df_raw.empty:
        risk_analysis.show_page(df_raw)
    else:
        st.warning("Could not load data for analysis. Please check the database connection.")