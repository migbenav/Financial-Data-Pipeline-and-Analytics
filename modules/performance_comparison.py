# modules/performance_comparison.py
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

def show_page(df):
    # Ensure the timestamp column is in datetime format
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    st.markdown("""
        <h1 style='text-align: center; color: #2980b9;'>Financial Data & Analytics Dashboard</h1>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("""
        <style>
        .centered-title-small {
            text-align: center !important;
            font-size: 2.1em !important;
            font-weight: bold;
        }
        </style>
        <h3 class="centered-title-small">Performance Comparison</h3>
    """, unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #7f8c8d;'>Compare the cumulative performance and key metrics of multiple assets.</p>", unsafe_allow_html=True)
    st.markdown("---")

    asset_list = sorted(df['symbol'].unique())
    selected_assets = st.multiselect("Select assets to compare:", asset_list, default=asset_list)
    
    if not selected_assets:
        st.warning("Please select at least one asset to compare.")
        return

    filtered_df = df[df['symbol'].isin(selected_assets)].copy()
    
    if filtered_df.empty:
        st.warning("No data available for the selected assets.")
        return
        
    # --- Plotting the Cumulative Performance ---
    st.subheader("Cumulative Performance Over Time")
    
    # Create an empty list to hold normalized data for each asset
    normalized_dfs = []
    
    for asset in selected_assets:
        asset_df = filtered_df[filtered_df['symbol'] == asset].set_index('timestamp').copy()
        
        # Resample to daily frequency and forward-fill missing values
        # asset_df_resampled = asset_df.resample('D').first().fillna(method='ffill')
        asset_df_resampled = asset_df.resample('D').first().ffill()

        # Normalize the prices based on the first available value
        initial_price = asset_df_resampled.iloc[0]['close_price']
        asset_df_resampled['normalized_price'] = asset_df_resampled['close_price'] / initial_price
        asset_df_resampled['symbol'] = asset
        
        normalized_dfs.append(asset_df_resampled.reset_index())
    
    # Concatenate all normalized DataFrames into a single one
    if not normalized_dfs:
        st.warning("No data found for the selected assets after processing.")
        return
    
    combined_normalized_df = pd.concat(normalized_dfs)
    
    # Create the plot
    fig = px.line(combined_normalized_df, x='timestamp', y='normalized_price', color='symbol',
                  title="Cumulative Performance of Selected Assets",
                  labels={'normalized_price': 'Normalized Performance (Start = 1.0)', 'timestamp': 'Date'})
    fig.update_layout(xaxis_title="Date", yaxis_title="Cumulative Performance (Normalized)",
                      hovermode="x unified", legend_title_text="Asset")
    #st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': True})

    st.markdown("---")
    
    # --- Performance Metrics Summary Table ---
    st.subheader("Performance Metrics Summary")
    
    metrics_data = []
    for asset in selected_assets:
        asset_df = filtered_df[filtered_df['symbol'] == asset].copy()
        
        if asset_df.empty or len(asset_df) < 2:
            continue
            
        returns = asset_df['close_price'].pct_change().dropna()
        
        # Total Return
        total_return = (asset_df['close_price'].iloc[-1] / asset_df['close_price'].iloc[0]) - 1
        
        # Annualized Return
        days = (asset_df['timestamp'].iloc[-1] - asset_df['timestamp'].iloc[0]).days
        annualized_return = (1 + total_return) ** (365 / days) - 1 if days > 0 else 0
        
        # Annualized Volatility
        volatility = returns.std() * np.sqrt(252)
        
        metrics_data.append({
            "Asset": asset,
            "Total Return": total_return,
            "Annualized Return": annualized_return,
            "Annualized Volatility": volatility
        })
    
    metrics_df = pd.DataFrame(metrics_data)
    
    # Format the table before displaying
    display_metrics_df = metrics_df.copy()
    display_metrics_df["Total Return"] = display_metrics_df["Total Return"].apply(lambda x: f"{x:,.2%}")
    display_metrics_df["Annualized Return"] = display_metrics_df["Annualized Return"].apply(lambda x: f"{x:,.2%}")
    display_metrics_df["Annualized Volatility"] = display_metrics_df["Annualized Volatility"].apply(lambda x: f"{x:,.2%}")
    st.dataframe(display_metrics_df, width='stretch', hide_index=True)
    