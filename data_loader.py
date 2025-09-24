# data_loader.py

import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os
from psycopg2.extras import execute_values
from datetime import datetime, timedelta, date
from typing import Optional
from api_fetchers import AlphaVantageFetcher, YahooFinanceFetcher, CoinMarketCapFetcher

# This file must load the environment variables itself
load_dotenv()

def init_connection():
    """Initializes a connection to the Supabase database."""
    try:
        db_url = os.environ.get('SUPABASE_DB_URL')
        return psycopg2.connect(db_url)
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

def get_data() -> pd.DataFrame:
    """Fetches all data from the stock_prices table."""
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

def get_latest_date(symbol: str) -> Optional[datetime.date]:
    """Fetches the latest timestamp for a given symbol from the database."""
    conn = init_connection()
    if conn is None:
        return None
    try:
        with conn.cursor() as cur:
            query = "SELECT MAX(timestamp) FROM stock_prices WHERE symbol = %s;"
            cur.execute(query, (symbol,))
            result = cur.fetchone()[0]
            if result:
                # result is already a date object, no need to call .date() again
                return result
            return None
    except Exception as e:
        print(f"Error fetching latest date for {symbol}: {e}")
        return None
    finally:
        if conn:
            conn.close()

def load_data(
    fetcher_class,
    assets: list,
    historical: bool = False,
    custom_start_date: Optional[date] = None, # NEW: Optional custom start date
    custom_end_date: Optional[date] = None     # NEW: Optional custom end date
):
    """
    Loads data for a list of assets using a specified fetcher class.
    """
    conn = init_connection()
    if conn is None:
        return
    
    alpha_vantage_api_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
    coin_market_api_key = os.environ.get('COIN_MARKET_API_KEY')

    for symbol in assets:
        if custom_start_date:
            # If a custom start date is provided, use it, and the custom end date if available
            start_date = custom_start_date
            end_date = custom_end_date if custom_end_date else datetime.now().date()
            print(f"Custom load for {symbol} from {start_date} to {end_date}...")
        elif historical:
            # Historical load from 2005-01-01
            start_date = date(2005, 1, 1)
            end_date = None
            print(f"Performing initial historical load for {symbol}...")
        else:
            # Incremental update based on latest DB record
            latest_date = get_latest_date(symbol)
            if latest_date:
                start_date = latest_date + timedelta(days=1)
                end_date = datetime.now().date()
                print(f"Updating data for {symbol} from {start_date} to {end_date}...")
            else:
                start_date = date(2005, 1, 1)
                end_date = None
                print(f"Performing initial historical load for {symbol}...")

        # Pass the api_key if the fetcher needs it
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
        else:
            fetcher = fetcher_class(symbol)

        if isinstance(fetcher, AlphaVantageFetcher):
            # AlphaVantageFetcher uses 'full' for historical (start_date is date(2005, 1, 1))
            # or 'compact' for the latest (start_date is latest_date + 1 day).
            # The logic here is simplified: if start_date is the historical start, use 'full'.
            # Note: custom_start_date will still result in an API call unless it's a small range
            # that 'compact' can cover. For AlphaVantage, we'll maintain the historical flag logic
            # for now, as it doesn't natively support range queries like Yahoo Finance.
            is_full_historical = (start_date == date(2005, 1, 1)) and (not custom_start_date)
            df = fetcher.fetch_data(asset_type='stocks', historical=is_full_historical)
        elif isinstance(fetcher, YahooFinanceFetcher):
            # YahooFinanceFetcher supports start_date and end_date for range queries
            df = fetcher.fetch_data(start_date=start_date, end_date=end_date)
        elif isinstance(fetcher, CoinMarketCapFetcher):
            # CoinMarketCapFetcher only provides the latest snapshot, range is not supported
            df = fetcher.fetch_data()
        else:
            print(f"No fetcher configured for {type(fetcher)}.")
            continue
        
        if df.empty:
            print(f"No new data retrieved for {symbol}. Skipping insertion.")
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