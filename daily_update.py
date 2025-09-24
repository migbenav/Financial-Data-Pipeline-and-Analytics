# daily_update.py
# This script is designed to be executed daily to update the database
# with the most recent financial data.

from data_loader import load_data
from api_fetchers import AlphaVantageFetcher, CoinMarketCapFetcher

# Define the assets
stocks = ['MSFT', 'KO', 'JPM', 'GLD', 'SLV']
cryptos = ['BTC', 'ETH']

# Run the daily update for stocks
print("Starting daily update for stocks...")
load_data(AlphaVantageFetcher, stocks)

# Run the daily update for cryptos
print("Starting daily update for cryptos...")
load_data(CoinMarketCapFetcher, cryptos)

print("Daily update complete.")