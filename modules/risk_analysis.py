# modules/risk_analysis.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def show_page(df):
    st.markdown("""
        <h1 style='text-align: center; color: #2980b9;'>Financial Data & Analytics Dashboard</h1>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.title("Financial Risk Analysis", anchor=False)
    st.markdown("<p style='text-align: center; color: #7f8c8d;'>Explore key risk metrics like annualized volatility and max drawdown for various assets.</p>", unsafe_allow_html=True)
    
    def calculate_risk_metrics(df):
        """Calculates annualized volatility and max drawdown for all assets."""
        metrics = {}
        for symbol in df['symbol'].unique():
            asset_df = df[df['symbol'] == symbol].copy()
            asset_df.set_index('timestamp', inplace=True)
            returns = asset_df['close_price'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)
            cumulative_returns = (1 + returns).cumprod()
            peak = cumulative_returns.cummax()
            drawdown = (cumulative_returns - peak) / peak
            max_drawdown = drawdown.min()
            metrics[symbol] = {'Volatility': volatility, 'Max Drawdown': max_drawdown}
        return metrics

    risk_metrics = calculate_risk_metrics(df)
    metrics_df = pd.DataFrame.from_dict(risk_metrics, orient='index')
    metrics_df = metrics_df.reset_index().rename(columns={'index': 'Asset'})
    
    # Sort the table by Max Drawdown (from least to most risky)
    metrics_df = metrics_df.sort_values(by='Max Drawdown', ascending=True)

    st.subheader("Asset Risk Comparison")
    
    # Format the DataFrame columns to strings with percentage signs
    display_df = metrics_df.copy()
    display_df['Volatility'] = display_df['Volatility'].apply(lambda x: f"{x:,.2%}")
    display_df['Max Drawdown'] = display_df['Max Drawdown'].apply(lambda x: f"{x:,.2%}")
    
    # Display the formatted DataFrame
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    st.markdown("---")
    
    st.subheader("Visualize Volatility & Drawdown")
    
    # Calculate the average values to create the quadrant lines
    avg_volatility = metrics_df['Volatility'].mean()
    avg_drawdown = metrics_df['Max Drawdown'].mean()

    fig = px.scatter(
        metrics_df,
        x='Volatility',
        y='Max Drawdown',
        color='Asset',
        size='Volatility',
        hover_data={'Volatility': ':.2%', 'Max Drawdown': ':.2%'},
        title="Volatility vs. Max Drawdown by Asset"
    )

    # Correctly define axis ranges to prevent the 'NoneType' error
    # We add a small buffer (10%) to the min/max values for better visualization
    volatility_range = [
        metrics_df['Volatility'].min() * 0.9,
        metrics_df['Volatility'].max() * 1.1
    ]
    drawdown_range = [
        metrics_df['Max Drawdown'].min() * 1.1,
        metrics_df['Max Drawdown'].max() * 0.9
    ]

    fig.update_xaxes(range=volatility_range)
    fig.update_yaxes(range=drawdown_range)

    # Add horizontal and vertical lines for the quadrants
    fig.add_shape(
        type="line",
        x0=avg_volatility, y0=drawdown_range[0],
        x1=avg_volatility, y1=drawdown_range[1],
        line=dict(color="White", width=1, dash="dash"),
        name="Average Volatility"
    )
    fig.add_shape(
        type="line",
        x0=volatility_range[0], y0=avg_drawdown,
        x1=volatility_range[1], y1=avg_drawdown,
        line=dict(color="White", width=1, dash="dash"),
        name="Average Drawdown"
    )

    fig.update_layout(xaxis_tickformat=",.2%", yaxis_tickformat=",.2%")
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})