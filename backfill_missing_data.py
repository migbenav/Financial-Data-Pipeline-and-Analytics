# backfill_missing_data.py

"""
File: backfill_missing_data.py
Function:
    This script is designed to perform a backfill operation on the database,
    loading any missing historical data for specified financial assets. It uses
    YahooFinanceFetcher for cryptocurrencies and AlphaVantageFetcher for stocks
    to ensure the data is complete from the initial historical start date (2005-01-01)
    up to the current date.

Functions Contained:
    - main: Coordinates the data loading process for stocks and cryptocurrencies.

Function Descriptions:
    - main:
        - Purpose: Primary function to execute the backfill logic.
        - Related Elements: Utilizes load_data from data_loader.py and AlphaVantageFetcher/
          YahooFinanceFetcher from api_fetchers.py.
"""

from datetime import date
from data_loader import load_data
from api_fetchers import AlphaVantageFetcher, YahooFinanceFetcher

def main():
    """
    Purpose: Main function to execute the backfill process for stocks and cryptos.
    Inputs: None
    Outputs: None (The function executes the load_data process which commits data to the database)
    """
    # Define the assets for backfill (should match daily_update.py where possible)
    # Using the fetchers that support historical/range data for backfill

    #stocks = ['MSFT', 'KO', 'JPM', 'GLD', 'SLV']

    # NOTE: Using YahooFinanceFetcher for crypto backfill as it handles historical ranges well.
    cryptos = ['BTC', 'ETH'] 

    START_DATE = date(2025, 9, 24)
    END_DATE = date(2025, 9, 25)

    # --- Backfill for Stocks (using AlphaVantageFetcher) ---
    #print("Starting backfill for STOCKS using AlphaVantageFetcher...")
    # load_data will calculate the missing date range automatically by checking the latest date.
    #load_data(AlphaVantageFetcher, stocks, historical=False, custom_start_date=START_DATE, custom_end_date=END_DATE)
    #print("Stock backfill complete.")
    
    # --- Backfill for Cryptos (using YahooFinanceFetcher) ---
    print("\nStarting backfill for CRYPTOS using YahooFinanceFetcher...")
    # YahooFinanceFetcher is better suited for historical/range loading for cryptos.
    load_data(YahooFinanceFetcher, cryptos, historical=False, custom_start_date=START_DATE, custom_end_date=END_DATE)
    print("Crypto backfill complete.")


if __name__ == "__main__":
    main()