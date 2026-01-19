import yfinance as yf

# Get stock info
apple = yf.Ticker("AAPL")

# Current price and basic info
try:
    print("Current AAPL Price:", apple.info.get('currentPrice', 'N/A'))
    print("AAPL Market Cap:", apple.info.get('marketCap', 'N/A'))
except Exception as e:
    print(f"Error fetching stock info: {e}")

# Historical data
print("\nHistorical Data (1 month):")
try:
    hist = apple.history(period="1mo")  # last month
    print(hist)
except Exception as e:
    print(f"Error fetching historical data: {e}")

# Download multiple stocks
print("\nMulti-Stock Comparison (1 year - Closing Prices):")
try:
    data = yf.download("AAPL MSFT GOOGL", period="1y")
    if not data.empty and 'Close' in data.columns.get_level_values(0):
        print(data['Close'])
    else:
        print("No data available")
except Exception as e:
    print(f"Error downloading multi-stock data: {e}")
