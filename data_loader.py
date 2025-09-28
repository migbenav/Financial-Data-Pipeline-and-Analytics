# data_loader.py
"""
File: data_loader.py
Function:
    This file manages all database connection and data loading logic. It handles 
    fetching data from external APIs and inserting/updating records in the database.
    It includes robust logic to determine the appropriate start date for updates 
    (latest date in DB, full historical, or custom date range). It also features 
    dual environment compatibility for secrets management (local .env or Streamlit Cloud).

Functions Contained:
    - get_secret: Retrieves environment variables from local or Streamlit secrets.
    - init_connection: Initializes the connection to the PostgreSQL database.
    - get_data: Fetches all data from the stock_prices table.
    - get_latest_date: Finds the latest recorded date for a given symbol.
    - load_data: Main orchestration function for fetching and loading data.

Function Descriptions:
    - get_secret:
        - Purpose: Auxiliary function to safely read environment variables/secrets.
        - Related Elements: os, dotenv, streamlit.
    - init_connection:
        - Purpose: Primary function to establish database connection.
        - Related Elements: psycopg2, get_secret.
    - get_data:
        - Purpose: Retrieves all historical data from the database.
        - Related Elements: pandas.
    - get_latest_date:
        - Purpose: Utility function to find the most recent timestamp for an asset.
        - Related Elements: psycopg2, date.
    - load_data:
        - Purpose: Main function for fetching and persisting data using various fetcher classes.
        - Related Elements: AlphaVantageFetcher, YahooFinanceFetcher, CoinMarketCapFetcher, datetime.
"""

import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os
from psycopg2.extras import execute_values
from datetime import datetime, timedelta, date
from typing import Optional, Type
from api_fetchers import AlphaVantageFetcher, YahooFinanceFetcher, CoinMarketCapFetcher

# We execute load_dotenv() immediately. This populates os.environ locally.
load_dotenv() 

# We detect if Streamlit is available for later access to st.secrets.
try:
    import streamlit as st
    STREAMLIT_ENV = True
except ImportError:
    STREAMLIT_ENV = False

    
def get_secret(key: str) -> Optional[str]:
    """
    Purpose: Auxiliary function to retrieve a secret/environment variable.
             It prioritizes os.environ (local .env) over st.secrets (Cloud).
    Inputs (Inputs):
        - key (str): The name of the secret/environment variable.
    Outputs (Outputs): The secret value as a string, or None if not found.
    """
    
    # 1. CHECK OS.ENVIRON (Local .env priority)
    # If the key is found here, it's either from the local .env file or a standard OS variable.
    local_value = os.environ.get(key)
    if local_value:
        return local_value

    # 2. CHECK STREAMLIT SECRETS (Cloud priority, only if not found locally)
    if STREAMLIT_ENV and hasattr(st, 'secrets'):
        # Check if Streamlit has the secret (this is where Cloud secrets live)
        cloud_value = st.secrets.get(key)
        if cloud_value:
             return cloud_value

    return None


def init_connection():
    """
    Purpose: Primary function to establish database connection.
    Inputs (Inputs): None
    Outputs (Outputs): A psycopg2 connection object or None if connection fails.
    """
    try:
        # Use the unified getter function
        db_url = get_secret('SUPABASE_DB_URL')
        if not db_url:
            print("Error: SUPABASE_DB_URL not found. Check .env (local) or Streamlit Secrets (cloud).")
            return None
            
        return psycopg2.connect(db_url)
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

def get_data() -> pd.DataFrame:
    """
    Purpose: Retrieves all historical data from the stock_prices table.
    Inputs (Inputs): None
    Outputs (Outputs): A pandas DataFrame with all data, or an empty DataFrame on failure.
    """
    conn = init_connection()
    if conn is None:
        return pd.DataFrame()
    try:
        query = "SELECT timestamp, symbol, open_price, high_price, low_price, close_price, volume FROM stock_prices ORDER BY timestamp ASC;"
        df = pd.read_sql(query, conn)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        print(f"Error fetching data from the database: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

def get_latest_date(symbol: str) -> Optional[date]:
    """
    Purpose: Utility function to find the most recent timestamp for a given asset symbol.
    Inputs (Inputs): 
        - symbol (str): The asset symbol (e.g., 'BTC', 'MSFT').
    Outputs (Outputs): The latest date object recorded for the symbol, or None if no data is found.
    """
    conn = init_connection()
    if conn is None:
        return None
    try:
        with conn.cursor() as cur:
            # Fetches the latest timestamp from the database for the given symbol
            cur.execute("SELECT MAX(timestamp) FROM stock_prices WHERE symbol = %s;", (symbol,))
            latest_date_result = cur.fetchone()[0]
            return latest_date_result
    except Exception as e:
        # This handles errors like table not existing or connection issues
        print(f"Error retrieving latest date for {symbol}: {e}")
        return None
    finally:
        if conn:
            conn.close()

def load_data(
    fetcher_class: Type,
    assets: list,
    historical: bool = False,
    custom_start_date: Optional[date] = None, 
    custom_end_date: Optional[date] = None     
):
    """
    Purpose: Main function for fetching data from external APIs and loading it
             into the database. It handles both initial historical loading and
             incremental updates, supporting custom date ranges for backfill.
             Includes local filtering for fetchers (like AlphaVantage) that
             return more data than requested for incremental updates.
    Inputs (Inputs):
        - fetcher_class (Type): The class to use for fetching data (e.g., AlphaVantageFetcher).
        - assets (list): List of asset symbols (e.g., ['BTC', 'ETH']).
        - historical (bool): Flag to force a full historical load (starting from 2005-01-01).
        - custom_start_date (Optional[date]): Optional date to start fetching data from (overrides auto-calculation).
        - custom_end_date (Optional[date]): Optional date to end fetching data at.
    Outputs (Outputs): None (Data is committed directly to the database).
    """
    conn = init_connection()
    if conn is None:
        return
    
    # Use the unified getter function for API keys
    alpha_vantage_api_key = get_secret('ALPHA_VANTAGE_API_KEY')
    coin_market_api_key = get_secret('COIN_MARKET_API_KEY')

    for symbol in assets:
        
        # --- 1. Determine the start, end, and filter dates ---
        
        filter_date = None
        latest_date_db = get_latest_date(symbol)
        
        if custom_start_date:
            # Mode: Custom load for targeted backfill
            start_date = custom_start_date
            end_date = custom_end_date if custom_end_date else datetime.now().date()
            print(f"Custom load for {symbol} from {start_date} to {end_date}...")
            
        elif historical or not latest_date_db:
            # Mode: Full historical load (forced or no data found)
            start_date = date(2005, 1, 1)
            end_date = None
            if historical:
                print(f"Performing initial historical load (forced) for {symbol}...")
            else:
                print(f"No previous data found. Starting full historical load for {symbol}...")
                
        else:
            # Mode: Incremental update based on latest DB record
            # filter_date will be used to discard existing records returned by the API
            filter_date = latest_date_db
            
            # Start fetching from the day after the last recorded date
            start_date = latest_date_db + timedelta(days=1)
            end_date = datetime.now().date()
            print(f"Updating data for {symbol} from {start_date} to {end_date} (Latest in DB: {latest_date_db})...")


        # --- 2. Instantiate the fetcher ---
        
        if fetcher_class == AlphaVantageFetcher:
            if not alpha_vantage_api_key:
                print("ALPHA_VANTAGE_API_KEY not found. Skipping Alpha Vantage assets.")
                continue
            fetcher = fetcher_class(symbol, api_key=alpha_vantage_api_key)

        elif fetcher_class == CoinMarketCapFetcher:
            if not coin_market_api_key:
                print("COIN_MARKET_API_KEY not found. Skipping CoinMarketCap assets.")
                continue
            fetcher = fetcher_class(symbol, api_key=coin_market_api_key)
            
        elif fetcher_class == YahooFinanceFetcher:
            fetcher = fetcher_class(symbol)

        else:
            print(f"No fetcher configured for {fetcher_class.__name__}.")
            continue

        
        # --- 3. Fetch the data ---
        
        df = pd.DataFrame()
        if isinstance(fetcher, AlphaVantageFetcher):
            # AlphaVantage logic remains focused on full/compact output sizes.
            # If we're updating, we rely on 'compact' (latest ~100 days),
            # which requires post-fetch filtering (using filter_date).
            is_full_historical_av = (start_date == date(2005, 1, 1)) and (not custom_start_date)
            df = fetcher.fetch_data(asset_type='stocks', historical=is_full_historical_av)

        elif isinstance(fetcher, YahooFinanceFetcher):
            # YahooFinanceFetcher supports start_date and end_date for range queries,
            # so the data returned should already be filtered.
            df = fetcher.fetch_data(start_date=start_date, end_date=end_date)

        elif isinstance(fetcher, CoinMarketCapFetcher):
            # CoinMarketCapFetcher only provides the latest snapshot.
            df = fetcher.fetch_data()
            
            
        # --- 3.5. Local Filtering for Incremental Updates (Crucial Fix) ---
        if not df.empty and filter_date:
            original_size = len(df)
            
            # Convert timestamp column to date object for comparison
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.date
            
            # Filter the DataFrame to keep only records strictly newer than the latest DB date
            df = df[df['timestamp'] > filter_date]
            
            if len(df) < original_size:
                print(f"Filtered {original_size - len(df)} redundant records for {symbol} using local date filter.")


        # --- 4. Insert data ---
        
        if df.empty:
            print(f"No new data retrieved for {symbol} within the target range. Skipping insertion.")
            continue

        data_to_insert = [
            (
                row['timestamp'],
                row['symbol'],
                row['open_price'],
                row['high_price'],
                row['low_price'],
                row['close_price'],
                row['volume'],
                datetime.now()
            )
            for _, row in df.iterrows()
        ]

        try:
            with conn.cursor() as cur:
                execute_values(cur, """
                    INSERT INTO stock_prices (timestamp, symbol, open_price, high_price, low_price, close_price, volume, load_timestamp)
                    VALUES %s
                    ON CONFLICT (timestamp, symbol) DO UPDATE SET
                        open_price = EXCLUDED.open_price,
                        high_price = EXCLUDED.high_price,
                        low_price = EXCLUDED.low_price,
                        close_price = EXCLUDED.close_price,
                        volume = EXCLUDED.volume,
                        load_timestamp = EXCLUDED.load_timestamp;
                """, data_to_insert)
                conn.commit()
            print(f"Successfully inserted/updated {len(data_to_insert)} rows for {symbol}.")
        except Exception as e:
            print(f"An error occurred while inserting data for {symbol}: {e}")
            conn.rollback()

    if conn:
        conn.close()