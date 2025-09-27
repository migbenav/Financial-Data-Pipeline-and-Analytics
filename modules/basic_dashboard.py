# modules/basic_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta


def display_analytics(df):
    """
    Calculates and displays key analytics for the selected asset.
    """
    st.markdown("""
        <style>
        div[data-testid="stMetricValue"] {
            font-size: 1.5rem; /* Adjust this value as needed */
        }
        </style>
    """, unsafe_allow_html=True)

    st.subheader("Key Statistics & Analytics")

    df_sorted = df.sort_values(by='timestamp', ascending=True)
    if df_sorted.empty:
        st.warning("No data available to display analytics.")
        return
        
    latest_close = df_sorted.iloc[-1]['close_price']
    latest_timestamp = df_sorted.iloc[-1]['timestamp']

    # --- ROW 1: PRICE CHANGES (4 columns) ---
    col1, col2, col3, col4 = st.columns(4)
    
    # Yesterday's change
    if len(df_sorted) > 1:
        prev_close_day = df_sorted.iloc[-2]['close_price']
        change_day = ((latest_close - prev_close_day) / prev_close_day) * 100
        delta_day = latest_close - prev_close_day
        # Pass raw delta for color/arrow, but a formatted value to the delta string.
        col1.metric(label="24h Change", value=f"{change_day:,.2f}%", delta=f"{delta_day:,.2f}")
    
    # Weekly change
    weekly_ago_df = df_sorted[df_sorted['timestamp'] <= (latest_timestamp - timedelta(days=7))]
    if not weekly_ago_df.empty:
        prev_close_week = weekly_ago_df.iloc[-1]['close_price']
        change_week = ((latest_close - prev_close_week) / prev_close_week) * 100
        delta_week = latest_close - prev_close_week
        col2.metric(label="1W Change", value=f"{change_week:,.2f}%", delta=f"{delta_week:,.2f}")

    # Monthly change
    monthly_ago_df = df_sorted[df_sorted['timestamp'] <= (latest_timestamp - timedelta(days=30))]
    if not monthly_ago_df.empty:
        prev_close_month = monthly_ago_df.iloc[-1]['close_price']
        change_month = ((latest_close - prev_close_month) / prev_close_month) * 100
        delta_month = latest_close - prev_close_month
        col3.metric(label="1M Change", value=f"{change_month:,.2f}%", delta=f"{delta_month:,.2f}")

    # Year-to-date change
    start_of_year_df = df_sorted[df_sorted['timestamp'].dt.year == latest_timestamp.year]
    if not start_of_year_df.empty:
        ytd_start_price = start_of_year_df.iloc[0]['close_price']
        change_ytd = ((latest_close - ytd_start_price) / ytd_start_price) * 100
        delta_ytd = latest_close - ytd_start_price
        col4.metric(label="YTD Change", value=f"{change_ytd:,.2f}%", delta=f"{delta_ytd:,.2f}")
    
    st.markdown("---")
    
    # --- ROW 2: MIN/MAX WEEKLY & MONTHLY (4 columns) ---
    col5, col6, col7, col8 = st.columns(4)
    week_df = df_sorted[df_sorted['timestamp'] >= (latest_timestamp - timedelta(days=7))]
    if not week_df.empty:
        max_week = week_df['high_price'].max()
        min_week = week_df['low_price'].min()
        col5.metric(label="1W Min", value=f"${min_week:,.2f}")
        col6.metric(label="1W Max", value=f"${max_week:,.2f}")
    
    month_df = df_sorted[df_sorted['timestamp'] >= (latest_timestamp - timedelta(days=30))]
    if not month_df.empty:
        max_month = month_df['high_price'].max()
        min_month = month_df['low_price'].min()
        col7.metric(label="1M Min", value=f"${min_month:,.2f}")
        col8.metric(label="1M Max", value=f"${max_month:,.2f}")

    # --- ROW 3: MIN/MAX YEARLY & ALL-TIME (4 columns) ---
    col9, col10, col11, col12 = st.columns(4)
    year_df = df_sorted[df_sorted['timestamp'].dt.year == latest_timestamp.year]
    if not year_df.empty:
        max_year = year_df['high_price'].max()
        min_year = year_df['low_price'].min()
        col9.metric(label="1Y Min", value=f"${min_year:,.2f}")
        col10.metric(label="1Y Max", value=f"${max_year:,.2f}")

    max_all = df_sorted['high_price'].max()
    min_all = df_sorted['low_price'].min()
    col11.metric(label="All-Time Min", value=f"${min_all:,.2f}")
    col12.metric(label="All-Time Max", value=f"${max_all:,.2f}")
    
    st.markdown("---")
    
def show_page(df):
    st.markdown("""
        <h1 style='text-align: center; color: #2980b9;'>Financial Data & Analytics Dashboard</h1>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    asset_list = df['symbol'].unique()
    selected_asset = st.selectbox("Select an asset to visualize:", asset_list)
    
    # Filter and sort the DataFrame
    filtered_df = df[df['symbol'] == selected_asset].sort_values(by='timestamp', ascending=False)
    
    # Display Analytics Section
    display_analytics(filtered_df)
    
    # Prepare DataFrame for display with custom formatting
    st.subheader(f"Recent Data for {selected_asset}")
    display_df = filtered_df.copy()
    
    # Calculate daily price change
    display_df['daily_change_pct'] = display_df['close_price'].pct_change(-1) * 100
    
    # Apply number formatting
    display_df['open_price'] = display_df['open_price'].apply(lambda x: f"${x:,.2f}")
    display_df['high_price'] = display_df['high_price'].apply(lambda x: f"${x:,.2f}")
    display_df['low_price'] = display_df['low_price'].apply(lambda x: f"${x:,.2f}")
    display_df['close_price'] = display_df['close_price'].apply(lambda x: f"${x:,.2f}")
    display_df['volume'] = display_df['volume'].apply(lambda x: f"{x:,.0f}")
    
    # New trend column with formatted percentage and color
    display_df['Price Change %'] = display_df['daily_change_pct'].apply(
        lambda x: f"▲ {x:,.2f}%" if x > 0 else f"▼ {x:,.2f}%" if x < 0 else f"{x:,.2f}%"
    )

    # Use Pandas Style to color the cells and hide the index
    def color_change(val):
        """Applies color to cells based on the value."""
        if isinstance(val, str):
            val = float(val.replace('▲ ', '').replace('▼ ', '').replace('%', ''))
        
        if val > 0:
            color = 'green'
        elif val < 0:
            color = 'red'
        else:
            color = 'black'
        return f'color: {color}'

    # Create a list of the columns you want to display
    columns_to_display = ["timestamp", "open_price", "close_price", "high_price", "low_price", "volume", "Price Change %"]

    # Select the desired columns FIRST, then take the head, apply the style, and display.
    columns_to_display = ["timestamp", "open_price", "close_price", "high_price", "low_price", "volume", "Price Change %"]
    styled_df = display_df[columns_to_display].head(20).style.map(color_change, subset=['Price Change %'])
    st.dataframe(styled_df, width='stretch', hide_index=True)
        
    # Subheader for the plot
    st.subheader(f"Closing Price Evolution for {selected_asset}", anchor=False)
    
    # Plotly figure
    fig = px.line(filtered_df.sort_values(by='timestamp', ascending=True),
                  x="timestamp", y="close_price", title=f"Closing Price of {selected_asset} Over Time")
    fig.update_traces(hovertemplate="<b>Date:</b> %{x}<br><b>Price:</b> $%{y:,.2f}")
    fig.update_layout(xaxis_rangeslider_visible=False, title={'x': 0.5, 'xanchor': 'center'}, hovermode="x unified")
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': True})