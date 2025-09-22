# modules/basic_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px

def show_page(df):
    st.markdown("""
        <h1 style='text-align: center; color: #2980b9;'>Financial Data & Analytics Dashboard</h1>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
        <h3 style='text-align: center; color: #f8f32b;'>Interactive Asset Price Analysis</h3>
    """, unsafe_allow_html=True)
    st.markdown("""
        This interactive application visualizes financial asset price data.
    """)
    asset_list = df['symbol'].unique()
    selected_asset = st.selectbox("Select an asset to visualize:", asset_list)
    filtered_df = df[df['symbol'] == selected_asset].sort_values(by='timestamp', ascending=False)
    st.subheader(f"Recent Data for {selected_asset}")
    display_df = filtered_df.copy()
    display_df['open_price'] = display_df['open_price'].apply(lambda x: f"${x:,.2f}")
    display_df['close_price'] = display_df['close_price'].apply(lambda x: f"${x:,.2f}")
    display_df['volume'] = display_df['volume'].apply(lambda x: f"{x:,.0f}")
    st.dataframe(display_df.head(20), use_container_width=True,
                 column_order=["timestamp", "open_price", "close_price", "volume"],
                 column_config={"timestamp": st.column_config.DatetimeColumn("Date"),
                                "open_price": st.column_config.TextColumn("Open Price"),
                                "close_price": st.column_config.TextColumn("Close Price"),
                                "volume": st.column_config.TextColumn("Volume")})
    st.subheader(f"Closing Price Evolution for {selected_asset}", anchor=False)
    fig = px.line(filtered_df.sort_values(by='timestamp', ascending=True),
                  x="timestamp", y="close_price", title=f"Closing Price of {selected_asset} Over Time")
    fig.update_traces(hovertemplate="<b>Date:</b> %{x}<br><b>Price:</b> $%{y:,.2f}")
    fig.update_layout(xaxis_rangeslider_visible=False, title={'x': 0.5, 'xanchor': 'center'}, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})