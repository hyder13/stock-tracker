import yfinance as yf
import json
from datetime import datetime
import os

def fetch_stock_prices():
    symbols = ["AAPL", "NVDA", "TSLA", "GOOGL", "MSFT", "AMZN"]
    data_file = "stock_data.json"
    
    # 讀取現有數據
    if os.path.exists(data_file):
        with open(data_file, "r") as f:
            all_data = json.load(f)
    else:
        all_data = {}

    today = datetime.now().strftime("%Y-%m-%d")
    print(f"Fetching data for {today}...")
    
    today_prices = {}
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            # 取得最新的收盤價
            price = ticker.fast_info['last_price']
            today_prices[symbol] = round(price, 2)
            print(f"{symbol}: {today_prices[symbol]}")
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
    
    if today_prices:
        all_data[today] = today_prices
        
        # 儲存回檔案
        with open(data_file, "w") as f:
            json.dump(all_data, f, indent=4)
        print("Data saved to stock_data.json")

if __name__ == "__main__":
    fetch_stock_prices()
