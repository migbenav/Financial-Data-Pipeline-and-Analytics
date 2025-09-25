# Data-Driven Financial Analysis Dashboard

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

---

## 4. Methodology: Data Pipeline (ETL)

This solution is built upon a robust data pipeline designed for consistency and reliability.

| Phase | Description | Technologies |
| :--- | :--- | :--- |
| **Data Ingestion** | Automated script collects daily historical pricing data for specified assets (stocks, crypto) from external financial APIs. | Python, Alpha Vantage API, Yahoo Finance API,  |
| **Data Storage** | Raw and processed data is stored in a cloud-based PostgreSQL database. | Supabase (PostgreSQL) |
| **Orchestration** | The data ingestion process is managed by a daily automated run. | GitHub Actions |
| **Feature Engineering** | Raw closing prices are used to calculate daily returns, moving averages (SMA), and risk metrics. | Python (Pandas) |

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