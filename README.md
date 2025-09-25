# Data-Driven Financial Analysis Dashboard

[![View the live Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://financial-data-pipeline-and-analytics.streamlit.app/) 

## 1. Executive Summary: Bridging Data and Investment Insights

This project demonstrates a complete, end-to-end analytical workflow for financial data. The primary objective is to transform raw asset pricing data into actionable insights by calculating key **Risk and Performance metrics**.

The solution features an automated data pipeline and a dynamic Streamlit dashboard, showcasing proficiency in data engineering, quantitative analysis, and data visualization to support strategic decision-making in asset comparison.

---

## 2. The Business Problem: Quantifying Risk and Performance

Modern investors require systematic tools to compare assets beyond simple price charts. This project addresses the challenge of providing a clear, objective assessment of assets by focusing on two core questions:

1.  **Systematic Risk Comparison:** How can we objectively compare the **volatility** and **downside risk** (Max Drawdown) of different asset types (e.g., stocks vs. cryptocurrencies)?
2.  **Performance Context:** How does the raw **Total Return** translate into **Annualized Performance** to allow for fair comparison across different timeframes?

---

## 3. Core Metrics: What We Calculate and Why

The value of this dashboard lies in explaining complex financial concepts through clear metrics:

| Metric | Calculation | Interpretation & Why It Matters |
| :--- | :--- | :--- |
| **Annualized Volatility** | Standard Deviation of daily returns, scaled to 252 trading days. | **Risk Measure:** Quantifies the asset's price fluctuation (risk). Higher volatility means greater uncertainty and wider price swings. |
| **Maximum Drawdown (Max DD)** | The largest peak-to-trough decline during a specific period. | **Downside Risk:** Measures the worst historical loss an investor would have suffered. Critical for assessing capital preservation. |
| **Annualized Return** | Total return, normalized to a one-year period. | **Performance Measure:** Allows fair comparison between two assets held for different durations (e.g., a stock held for 18 months vs. a crypto held for 6 months). |
| **Sharpe Ratio** | (Annualized Return - Risk-Free Rate) / Annualized Volatility. | **Risk-Adjusted Return:** Measures the return earned per unit of risk taken. A higher Sharpe Ratio is always desirable. |
| **Cumulative Return** | The total percentage change in value from the start to the end of the observation period.	| **Total Performance:** The actual gain or loss realized on an asset over the entire dataset history.|
| **VaR (Value at Risk) 95%** |	The 5th percentile of daily returns (negative value). |	**Short-Term Risk:** Estimates the maximum daily loss that should not be exceeded 95% of the time. Used for daily capital allocation.|
| **Winning Days %** |	Percentage of days where the asset's closing price increased (daily return > 0). |	**Consistency/Momentum:** Indicates how frequently the asset provides positive returns. A higher percentage suggests more consistent positive momentum.|

---

## 4. Methodology: Data Pipeline (ETL)

This solution is built upon a robust data pipeline designed for consistency and reliability.

| Phase | Description | Technologies |
| :--- | :--- | :--- |
| **Data Ingestion** | Automated script collects daily historical pricing data for specified assets. Note on APIs: Multiple fetchers are required due to API limitations: Yahoo Finance provides superior, reliable OHLC data for Cryptos (BTC, ETH), while Alpha Vantage is used for Stocks (MSFT, KO, etc.). | Python, Alpha Vantage API, Yahoo Finance API |
| **Data Storage** | Raw and processed data is stored in a cloud-based PostgreSQL database. | Supabase (PostgreSQL) |
| **Orchestration** | The data ingestion process is managed by a daily automated run. | GitHub Actions |

---

## 5. Dashboard Structure & Navigation (Streamlit)

The interactive dashboard is the final product, connected live to the PostgreSQL data pipeline.

Use the sidebar on the left to navigate between the sections:

* **Basic Dashboard:** View raw price charts, volume trends, and moving averages for individual asset selection.
* **Risk Analysis:** Visualizes the key trade-off between **Volatility** and **Max Drawdown** across all assets, segmented into performance quadrants.
* **Asset Comparison (Performance):** Tabular and graphical comparison of **Annualized Return** and **Risk Metrics** side-by-side for portfolio construction decisions.

---

## 6. Skills and Technologies

| Domain | Technologies / Concepts |
| :--- | :--- |
| **Data Engineering** | Python, PostgreSQL, Supabase, GitHub Actions, ETL |
| **Financial Analysis** | Volatility, Maximum Drawdown, Sharpe Ratio, Annualized Return |
| **Data Visualization** | Streamlit, Plotly, Pandas |
| **Project Management** | Problem Definition, Documentation (README), Version Control (Git) |

---

## 7. Getting Started: Setup and Dependencies

To run this dashboard locally and manage the data pipeline, you must complete the following steps:

1.  **Database Configuration (Supabase):**
    * Create a PostgreSQL database on Supabase and obtain your `SUPABASE_DB_URL`.
    * Initialize the data structure by executing the following SQL command to create the primary table:

        ```sql
        CREATE TABLE stock_prices (
            timestamp DATE NOT NULL,
            symbol VARCHAR(10) NOT NULL,
            open_price DOUBLE PRECISION,
            high_price DOUBLE PRECISION,
            low_price DOUBLE PRECISION,
            close_price DOUBLE PRECISION,
            volume BIGINT,
            load_timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
            PRIMARY KEY (timestamp, symbol)
        );
        ```

2.  **API Keys:** Obtain and configure the following keys in your local `.env` file (or Streamlit Secrets for cloud deployment):
    * `ALPHA_VANTAGE_API_KEY` (Required for stock data).
    * `COIN_MARKET_API_KEY` (Retained for potential future use or snapshot data).
    * `SUPABASE_DB_URL` (Connection string for the database).

3.  **Install Dependencies:** Run `pip install -r requirements.txt`.

4.  **Initial Data Population:**
    * The function `load_data` in `data_loader.py` handles the logic to determine which dates are missing.
    * Run the following script once to perform the **initial historical data load**. 
        ```bash
        python backfill_missing_data.py
        ```

---

## 8. Conclusions and Next Steps

### Conclusions
The current analysis successfully quantifies the trade-off between risk and performance. Assets like **GLD** and **KO** demonstrate significantly lower volatility and Max Drawdown compared to cryptocurrencies (BTC/ETH), which, despite offering high cumulative returns, expose an investor to substantial historical capital risk (as seen in the scatter plot). The **Sharpe Ratio** effectively highlights which asset provides the best return for the risk taken over the period.

### Future Work (Next Steps)
1.  **Time Window Analysis:** Implement date pickers in the dashboard to allow users to analyze risk and performance over custom rolling time windows (e.g., 3-year, 5-year).
2.  **Portfolio Optimization:** Integrate a **Monte Carlo Simulation** to suggest optimal asset allocations based on the calculated risk metrics.
3.  **Real-Time Monitoring:** Revisit the `CoinMarketCapFetcher` to display the **real-time price snapshot** (today's price) in the Overview page *alongside* the historical daily close, adding immediate market context.