import yfinance as yf

# Get stock info
apple = yf.Ticker("AAPL")

# Current price and basic info
print(apple.info['currentPrice'])
print(apple.info['marketCap'])

# Historical data
hist = apple.history(period="1mo")  # last month
print(hist)

# Download multiple stocks
data = yf.download("AAPL MSFT GOOGL", period="1y", auto_adjust=True)
print(data['Close'])
