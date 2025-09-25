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
    
    st.markdown("""
        <style>
        .centered-title-small {
            text-align: center !important;
            font-size: 2.1em !important; /* Adjust this value as needed */
            font-weight: bold;
        }
        </style>
        <h3 class="centered-title-small">Financial Risk Analysis</h3>
    """, unsafe_allow_html=True)

    st.markdown("<p style='text-align: center; color: #7f8c8d;'>Explore key risk metrics like annualized volatility and max drawdown for various assets.</p>", unsafe_allow_html=True)
    
    def calculate_risk_metrics(df):
        """Calculates annualized volatility, max drawdown, Sharpe Ratio, and other metrics for all assets."""
        metrics = {}
        # Assume a risk-free rate of 2%
        risk_free_rate = 0.02

        for symbol in df['symbol'].unique():
            asset_df = df[df['symbol'] == symbol].copy()
            asset_df.set_index('timestamp', inplace=True)
            returns = asset_df['close_price'].pct_change().dropna()
            
            # Skip if there's not enough data
            if returns.empty:
                continue
            
            # Annualized Volatility
            volatility = returns.std() * np.sqrt(252)
            
            # Max Drawdown
            cumulative_returns = (1 + returns).cumprod()
            peak = cumulative_returns.cummax()
            drawdown = (cumulative_returns - peak) / peak
            max_drawdown = drawdown.min()

            # Sharpe Ratio
            excess_returns = returns - (risk_free_rate / 252)
            sharpe_ratio = excess_returns.mean() / returns.std() * np.sqrt(252)

            # Cumulative Return
            total_cumulative_return = cumulative_returns.iloc[-1] - 1

            # VaR (Value at Risk) - 95% confidence level
            var_95 = returns.quantile(0.05)

            # Winning/Losing Days
            winning_days = (returns > 0).sum()
            losing_days = (returns < 0).sum()
            total_days = len(returns)
            winning_ratio = (winning_days / total_days) if total_days > 0 else 0

            metrics[symbol] = {
                'Volatility': volatility,
                'Max Drawdown': max_drawdown,
                'Sharpe Ratio': sharpe_ratio,
                'Cumulative Return': total_cumulative_return,
                'VaR (95%)': var_95,
                'Winning Days %': winning_ratio
            }
        return metrics

    risk_metrics = calculate_risk_metrics(df)
    metrics_df = pd.DataFrame.from_dict(risk_metrics, orient='index')
    metrics_df = metrics_df.reset_index().rename(columns={'index': 'Asset'})
    
    # Sort the table by Max Drawdown (from least to most risky)
    metrics_df = metrics_df.sort_values(by='Max Drawdown', ascending=True)

    st.subheader("Asset Risk Comparison")
    
    # Format the DataFrame columns
    display_df = metrics_df.copy()
    display_df['Volatility'] = display_df['Volatility'].apply(lambda x: f"{x:,.2%}")
    display_df['Max Drawdown'] = display_df['Max Drawdown'].apply(lambda x: f"{x:,.2%}")
    display_df['Sharpe Ratio'] = display_df['Sharpe Ratio'].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else "N/A")
    display_df['Cumulative Return'] = display_df['Cumulative Return'].apply(lambda x: f"{x:,.2%}")
    display_df['VaR (95%)'] = display_df['VaR (95%)'].apply(lambda x: f"{x:,.2%}")
    display_df['Winning Days %'] = display_df['Winning Days %'].apply(lambda x: f"{x:,.2%}")

    # Reorder the columns for better display
    display_df = display_df[['Asset', 'Volatility', 'Max Drawdown', 'Sharpe Ratio', 'Cumulative Return', 'VaR (95%)', 'Winning Days %']]
    
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
        hover_data={'Volatility': ':.2%', 'Max Drawdown': ':.2%', 'Sharpe Ratio': ':.2f', 'Cumulative Return': ':.2%'},
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
        line=dict(color="#555555", width=1, dash="dash"),
        name="Average Volatility"
    )
    fig.add_shape(
        type="line",
        x0=volatility_range[0], y0=avg_drawdown,
        x1=volatility_range[1], y1=avg_drawdown,
        line=dict(color="#555555", width=1, dash="dash"),
        name="Average Drawdown"
    )

    fig.update_layout(xaxis_tickformat=",.2%", yaxis_tickformat=",.2%")
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})