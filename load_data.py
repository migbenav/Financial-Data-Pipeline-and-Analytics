# load_data.py
"""
This script is designed for a one-time execution to perform a full historical
data load for all specified financial assets. It fetches all available historical
data from various APIs and populates the database.

It should be run only once to establish the initial dataset. For daily updates,
use the separate 'daily_update.py' script, which is optimized for efficiency
and only fetches new data.
"""

from data_loader import load_data
from api_fetchers import AlphaVantageFetcher, YahooFinanceFetcher

stocks = ['MSFT', 'KO', 'JPM', 'GLD', 'SLV']
cryptos = ['BTC', 'ETH']

# Load full historical stock data
#print("Starting initial historical load for stocks...")
#load_data(AlphaVantageFetcher, stocks, historical=True)

# Load full historical crypto data
print("Starting initial historical load for cryptos...")
load_data(YahooFinanceFetcher, cryptos, historical=True)

print("Historical data load complete.")