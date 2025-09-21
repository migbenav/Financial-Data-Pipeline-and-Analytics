# data_loader.py
import os
import requests
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time

class AlphaVantageDataLoader:
    """
    A class to fetch financial data from the Alpha Vantage API and load it into a PostgreSQL database.

    This class handles API requests, data parsing, and database insertion,
    with a focus on flexibility and error handling. It's designed to be
    reusable across different projects.

    Attributes:
        api_key (str): The Alpha Vantage API key.
        db_url (str): The Supabase/PostgreSQL database URL.
    """

    def __init__(self):
        """Initializes the data loader by loading environment variables."""
        load_dotenv()
        self.api_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
        self.db_url = os.environ.get('SUPABASE_DB_URL')

        if not self.api_key or not self.db_url:
            raise ValueError("API key and database URL must be set in the .env file.")

    # --- Auxiliary Functions ---
    def _get_api_url(self, asset_type: str, symbol: str, output_size: str) -> str:
        """
        Constructs the correct Alpha Vantage API URL based on the asset type.

        Args:
            asset_type (str): The type of asset ('stocks', 'crypto', 'forex').
            symbol (str): The ticker symbol for the asset.
            output_size (str): 'full' for historical data or 'compact' for recent data.

        Returns:
            str: The complete API URL.

        Raises:
            ValueError: If an invalid asset type is provided.
        """
        base_url = "https://www.alphavantage.co/query?"

        if asset_type == 'stocks':
            return f'{base_url}function=TIME_SERIES_DAILY&symbol={symbol}&outputsize={output_size}&apikey={self.api_key}'
        elif asset_type == 'crypto':
            # Note: Alpha Vantage requires 'market' for crypto data
            return f'{base_url}function=DIGITAL_CURRENCY_DAILY&symbol={symbol}&market=USD&apikey={self.api_key}'
        elif asset_type == 'forex':
            # Note: Forex data uses 'from_symbol' and 'to_symbol'
            return f'{base_url}function=FX_DAILY&from_symbol={symbol}&to_symbol=USD&apikey={self.api_key}'
        else:
            raise ValueError("Invalid asset type provided.")

    def _get_data_keys(self, asset_type: str):
        """
        Returns the correct API response keys based on the asset type.

        Args:
            asset_type (str): The type of asset ('stocks', 'crypto', 'forex').

        Returns:
            tuple: A tuple containing the time series key, open key, close key, and volume key.
        """
        if asset_type == 'stocks':
            return 'Time Series (Daily)', '1. open', '4. close', '5. volume'
        elif asset_type == 'crypto':
            return 'Time Series (Digital Currency Daily)', '1. open', '4. close', '5. volume'
        elif asset_type == 'forex':
            return 'Time Series FX (Daily)', '1. open', '4. close', None

    def _connect_to_db(self):
        """Establishes a connection to the PostgreSQL database."""
        return psycopg2.connect(self.db_url)

    # --- Main Functions ---
    def load_data(self, assets: dict, historical: bool = True, start_date: datetime = None):
        """
        Loads data for a specified list of assets into the database.

        This is the main public method. It iterates through asset types and
        symbols, fetches the data from the API, and inserts it into the database.

        Args:
            assets (dict): A dictionary where keys are asset types (e.g., 'stocks')
                           and values are lists of ticker symbols (e.g., ['MSFT', 'GOOGL']).
            historical (bool): If True, fetches full historical data. If False,
                               fetches recent data for daily updates.
            start_date (datetime): An optional datetime object to specify a start date
                                   for historical data. Data older than this date will be ignored.
        """
        output_size = 'full' if historical else 'compact'
        conn = None
        
        try:
            conn = self._connect_to_db()
            cur = conn.cursor()

            for asset_type, symbols in assets.items():
                for symbol in symbols:
                    print(f"Fetching {output_size} data for {symbol} ({asset_type})...")
                    url = self._get_api_url(asset_type, symbol, output_size)
                    response = requests.get(url)
                    time.sleep(1) # API rate limit

                    if response.status_code != 200:
                        print(f"Error for {symbol}. Status Code: {response.status_code}")
                        continue

                    data = response.json()
                    time_series_key, open_key, close_key, volume_key = self._get_data_keys(asset_type)

                    if time_series_key not in data:
                        print(f"Error: Could not retrieve data for {symbol}. Check API response.")
                        continue

                    time_series = data[time_series_key]

                    for timestamp_str, values in time_series.items():
                        try:
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d').date()
                            
                            if historical and start_date and timestamp < start_date.date():
                                continue

                            # Use .get() with a default value to avoid KeyErrors
                            open_price = float(values.get(open_key, 0))
                            close_price = float(values.get(close_key, 0))
                            volume = float(values.get(volume_key, 0)) if volume_key else 0
                            load_timestamp = datetime.now()

                            cur.execute(
                                "INSERT INTO stock_prices (timestamp, symbol, open_price, close_price, volume, load_timestamp) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (timestamp, symbol) DO UPDATE SET open_price = EXCLUDED.open_price, close_price = EXCLUDED.close_price, volume = EXCLUDED.volume, load_timestamp = EXCLUDED.load_timestamp",
                                (timestamp, symbol, open_price, close_price, volume, load_timestamp)
                            )
                        except Exception as e:
                            print(f"Error processing a data point for {symbol} on {timestamp_str}: {e}")
                            conn.rollback()
                            continue

                    print(f"Data for {symbol} saved successfully!")

            conn.commit()

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            if conn:
                cur.close()
                conn.close()

# --- Example Usage ---
if __name__ == "__main__":
    assets_to_load = {
        'stocks': ['MSFT', 'KO', 'JPM', 'GLD', 'SLV'],
        'crypto': ['BTC', 'ETH']
    }
    
    # Define the exact start date for the historical load
    start_date_specific = datetime(2005, 1, 1)
    
    # Example of fetching historical data, limited to the last 20 years from Jan 1, 2005
    loader = AlphaVantageDataLoader()
    loader.load_data(assets=assets_to_load, historical=True, start_date=start_date_specific)

    # Example of fetching recent data for daily updates
    # loader.load_data(assets=assets_to_load, historical=False)