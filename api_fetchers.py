import requests
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta, date
from typing import Optional

class AlphaVantageFetcher:
    """Fetches data from the Alpha Vantage API."""
    def __init__(self, symbol: str, api_key: str):
        self.symbol = symbol
        self.api_key = api_key

    def _get_api_url(self, asset_type: str, output_size: str) -> str:
        base_url = "https://www.alphavantage.co/query?"
        if asset_type == 'stocks':
            return f'{base_url}function=TIME_SERIES_DAILY&symbol={self.symbol}&outputsize={output_size}&apikey={self.api_key}'
        elif asset_type == 'crypto':
            return f'{base_url}function=DIGITAL_CURRENCY_DAILY&symbol={self.symbol}&market=USD&apikey={self.api_key}'
        else:
            raise ValueError("Invalid asset type provided.")

    def _get_data_keys(self, asset_type: str):
        if asset_type == 'stocks':
            return 'Time Series (Daily)', '1. open', '2. high', '3. low', '4. close', '5. volume'
        elif asset_type == 'crypto':
            return 'Time Series (Digital Currency Daily)', '1. open', '2. high', '3. low', '4. close', '5. volume'

    def fetch_data(self, asset_type: str, historical: bool = True) -> pd.DataFrame:
        output_size = 'full' if historical else 'compact'
        url = self._get_api_url(asset_type, output_size)
        response = requests.get(url)
        time.sleep(1)

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


class YahooFinanceFetcher:
    """Fetches historical data from Yahoo Finance."""
    def __init__(self, symbol: str):
        self.symbol = symbol

    def fetch_data(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> pd.DataFrame:
        """Fetches data and returns a DataFrame."""
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d') if end_date else datetime.now().strftime('%Y-%m-%d')

        try:
            if self.symbol in ['BTC', 'ETH']:
                ticker_symbol = f"{self.symbol}-USD"
            else:
                ticker_symbol = self.symbol
            
            ticker = yf.Ticker(ticker_symbol)
            df = ticker.history(start=start_date_str, end=end_date_str)
            
            if df.empty:
                print(f"No data found for {self.symbol} in the given date range.")
                return pd.DataFrame()

            df = df.reset_index()
            df = df.rename(columns={'Date': 'timestamp', 'Open': 'open_price', 'High': 'high_price', 'Low': 'low_price', 'Close': 'close_price', 'Volume': 'volume'})
            df['symbol'] = self.symbol
            return df[['timestamp', 'symbol', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']]
        
        except Exception as e:
            print(f"Error fetching data for {self.symbol}: {e}")
            return pd.DataFrame()


class CoinMarketCapFetcher:
    """Fetches real-time crypto data from the CoinMarketCap API."""
    
    def __init__(self, symbol: str, api_key: str):
        # CMC symbols are typically the base currency (e.g., BTC, not BTC-USD)
        self.symbol = symbol.replace('-USD', '') 
        self.original_symbol = symbol # Keep the original symbol for DB consistency
        self.api_key = api_key
        self.base_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

    def fetch_data(self) -> pd.DataFrame:
        """Fetches the latest snapshot price for the symbol."""
        if not self.api_key:
            print(f"Warning: CMC_API_KEY not configured. Skipping {self.original_symbol}.")
            return pd.DataFrame()
            
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
        }
        parameters = {
            'symbol': self.symbol,
            'convert': 'USD'
        }

        try:
            response = requests.get(self.base_url, headers=headers, params=parameters)
            response.raise_for_status() # Raise an exception for bad status codes
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from CoinMarketCap for {self.original_symbol}: {e}")
            return pd.DataFrame()
            
        # Check if symbol exists in data
        if self.symbol not in data['data']:
            print(f"Error: CoinMarketCap did not return data for {self.symbol}.")
            return pd.DataFrame()

        # Extract quote data
        asset_data = data['data'][self.symbol]
        quote = asset_data['quote']['USD']
        price = quote['price']
        timestamp = datetime.now()
        
        # Create a DataFrame for a single data point
        records = [{
            'timestamp': timestamp,
            'symbol': self.original_symbol, # Use original symbol for DB
            'open_price': price, # For a single snapshot, use price for OHLC
            'high_price': price,
            'low_price': price,
            'close_price': price,
            'volume': 0 # Volume data from CMC is complex, setting to 0 for simplicity
        }]

        return pd.DataFrame(records)