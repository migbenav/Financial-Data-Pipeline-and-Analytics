# api_fetchers.py
import requests
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

class APIFetcher:
    """Base class for all data fetchers."""
    def __init__(self, symbol: str):
        self.symbol = symbol

    def fetch_data(self, start_date: str = None, end_date: str = None, historical: bool = True) -> pd.DataFrame:
        """Fetches and returns data as a DataFrame."""
        raise NotImplementedError("This method must be implemented by a subclass.")

class AlphaVantageFetcher(APIFetcher):
    """Fetches data from the Alpha Vantage API."""
    def __init__(self, symbol: str, api_key: str):
        super().__init__(symbol)
        self.api_key = api_key

    def _get_api_url(self, asset_type: str, output_size: str) -> str:
        """Constructs the correct Alpha Vantage API URL."""
        base_url = "https://www.alphavantage.co/query?"
        if asset_type == 'stocks':
            return f'{base_url}function=TIME_SERIES_DAILY&symbol={self.symbol}&outputsize={output_size}&apikey={self.api_key}'
        elif asset_type == 'crypto':
            return f'{base_url}function=DIGITAL_CURRENCY_DAILY&symbol={self.symbol}&market=USD&apikey={self.api_key}'
        else:
            raise ValueError("Invalid asset type provided.")

    def _get_data_keys(self, asset_type: str):
        """Returns the correct API response keys."""
        if asset_type == 'stocks':
            # Updated keys to include high and low
            return 'Time Series (Daily)', '1. open', '2. high', '3. low', '4. close', '5. volume'
        elif asset_type == 'crypto':
            # Updated keys to include high and low
            return 'Time Series (Digital Currency Daily)', '1. open', '2. high', '3. low', '4. close', '5. volume'

    def fetch_data(self, asset_type: str, historical: bool = True) -> pd.DataFrame:
        """Fetches data and returns a DataFrame."""
        output_size = 'full' if historical else 'compact'
        url = self._get_api_url(asset_type, output_size)
        response = requests.get(url)
        time.sleep(1) # Respect API rate limits

        if response.status_code != 200:
            print(f"Error for {self.symbol}. Status Code: {response.status_code}")
            return pd.DataFrame()

        data = response.json()
        time_series_key, open_key, high_key, low_key, close_key, volume_key = self._get_data_keys(asset_type)

        if time_series_key not in data:
            print(f"Error: Could not retrieve data for {self.symbol}.")
            return pd.DataFrame()

        time_series = data[time_series_key]
        records = []
        for date_str, values in time_series.items():
            records.append({
                'timestamp': pd.to_datetime(date_str),
                'symbol': self.symbol,
                'open_price': float(values.get(open_key, 0)),
                'high_price': float(values.get(high_key, 0)),
                'low_price': float(values.get(low_key, 0)),
                'close_price': float(values.get(close_key, 0)),
                'volume': float(values.get(volume_key, 0))
            })
        return pd.DataFrame(records)

class YahooFinanceFetcher(APIFetcher):
    """Fetches historical data from Yahoo Finance."""
    def __init__(self, symbol: str):
        super().__init__(symbol)

    def fetch_data(self, start_date: datetime.date = None, end_date: datetime.date = None) -> pd.DataFrame:
        """Fetches data and returns a DataFrame."""
        if start_date is None or end_date is None:
            # Default behavior for historical load if dates are not provided
            start_date_str = '2005-01-01'
            end_date_str = datetime.now().strftime('%Y-%m-%d')
        else:
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')

        try:
            ticker = yf.Ticker(self.symbol)
            df = ticker.history(start=start_date_str, end=end_date_str)
            if df.empty:
                return pd.DataFrame()

            # Format the DataFrame to match the database schema
            df = df.reset_index()
            df = df.rename(columns={'Date': 'timestamp', 'Open': 'open_price', 'High': 'high_price', 'Low': 'low_price', 'Close': 'close_price', 'Volume': 'volume'})
            df['symbol'] = self.symbol
            return df[['timestamp', 'symbol', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']]
        except Exception as e:
            print(f"Error fetching data for {self.symbol}: {e}")
            return pd.DataFrame()