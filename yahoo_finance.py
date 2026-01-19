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
hist = apple.history(period="1mo")  # last month
print(hist)

# Download multiple stocks
print("\nMulti-Stock Comparison (1 year - Closing Prices):")
data = yf.download("AAPL MSFT GOOGL", period="1y")
print(data['Close'])
