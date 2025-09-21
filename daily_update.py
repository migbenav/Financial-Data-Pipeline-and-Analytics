# daily_update.py
# This script is designed to be executed daily to update the database
# with the most recent financial data.

from data_loader import AlphaVantageDataLoader

# List of assets to be updated.
# Commodities (GLD, SLV) are included in 'stocks' as they are ETFs and
# are handled the same way by the Alpha Vantage API.
assets_to_update = {
    'stocks': ['MSFT', 'KO', 'JPM', 'GLD', 'SLV'],
    'crypto': ['BTC', 'ETH']
}

# Create an instance of the data loader
loader = AlphaVantageDataLoader()

# Call the load function with `historical=False` to fetch only the latest data.
# The `on_conflict` clause in the SQL will handle updates for existing entries.
loader.load_data(assets=assets_to_update, historical=False)