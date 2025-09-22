# daily_update.py
# This script is designed to be executed daily to update the database
# with the most recent financial data.

# Call the load function with `historical=False` to fetch only the latest data.
# The `on_conflict` clause in the SQL will handle updates for existing entries.
loader.load_data(assets=assets_to_update, historical=False)

from data_loader import load_data
from api_fetchers import AlphaVantageFetcher, YahooFinanceFetcher

# Define the assets
stocks = ['MSFT', 'KO', 'JPM', 'GLD', 'SLV']
cryptos = ['BTC', 'ETH']

# Run the daily update for stocks (historical=False is now optional as the code handles it)
print("Starting daily update for stocks...")
load_data(AlphaVantageFetcher, stocks, asset_type='stocks', historical=False)

# Run the daily update for cryptos
print("Starting daily update for cryptos...")
load_data(YahooFinanceFetcher, cryptos, asset_type='crypto', historical=False)

print("Daily update complete.")