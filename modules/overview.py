# modules/overview.py
import streamlit as st

def show_page():
    st.markdown("""
        <h1 style='text-align: center; color: #2980b9;'>Financial Data & Analytics Dashboard</h1>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.write("""
    Welcome to the Financial Analytics Dashboard. This application is designed to analyze and visualize
    financial data from different assets, providing key insights into market behavior.
    """)
    st.subheader("Dashboard Sections")
    st.write("""
    Use the sidebar on the left to navigate between the different sections of the dashboard:
    
    - **Overview:** An introduction to the dashboard's purpose and functionalities.
    - **Basic Dashboard:** Explore key metrics and interactive charts for individual assets.
    - **Risk Analysis:** Dive into financial risk metrics such as annualized volatility and maximum drawdown.
    - **Asset Comparison (formerly Performance Comparison):** Compare the cumulative returns and key performance metrics of multiple selected assets.
    """)
    st.info("To get started, please select a page from the sidebar.")