from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import yfinance as yf
import json
import os
import time
from datetime import datetime, timedelta, timezone

app = Flask(__name__, static_folder='.')
CORS(app)

# 設定台灣時區 (UTC+8)
TW_TZ = timezone(timedelta(hours=8))

DATA_FILE = "stock_data.json"
CACHE_SECONDS = 300 # 5 分鐘

# 沿用你的觀察名單
WATCHLIST = [
    "NVDA", "TSLA", "MSTR", "AAPL", "AMD", "COIN", # 美股
    "2330.TW", "2317.TW", "2603.TW", "3231.TW", "2382.TW" # 台股
]

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/stock_data.json')
def get_static_json():
    return send_from_directory('.', 'stock_data.json')

def analyze_stock(symbol):
    print(f"Analyzing {symbol}...")
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        price = info.get('currentPrice') or info.get('regularMarketPrice')
        prev_close = info.get('previousClose')
        change = ((price - prev_close) / prev_close * 100) if price and prev_close else 0
        
        target_price = info.get('targetMeanPrice')
        recommendation = info.get('recommendationKey', 'N/A').replace('_', ' ').title()
        
        evaluation = ""
        if target_price and price:
            upside = ((target_price - price) / price) * 100
            if upside > 15 and recommendation in ['Buy', 'Strong Buy']:
                evaluation = f"分析師看好潛在漲幅 {upside:.1f}%，建議分批買進。"
            elif upside < 0:
                evaluation = "目前價格已高於分析師平均目標價，建議觀望或適度止盈。"
            else:
                evaluation = f"價格接近合理區間，目標價 ${target_price}。"
        else:
            evaluation = "目前缺乏足夠分析師數據，建議參考技術面走勢。"

        return {
            "symbol": symbol,
            "name": info.get('shortName', symbol),
            "price": price,
            "change": round(change, 2),
            "summary": (info.get('longBusinessSummary', '無')[:150] + "..."),
            "target_price": target_price,
            "recommendation": recommendation,
            "analyst_count": info.get('numberOfAnalystOpinions', 0),
            "inst_pct": round(info.get('heldPercentInstitutions', 0) * 100, 1),
            "evaluation": evaluation,
            "market": "台股" if symbol.endswith(".TW") else "美股"
        }
    except Exception as e:
        print(f"Error {symbol}: {e}")
        return None

def update_cache():
    results = []
    for symbol in WATCHLIST:
        data = analyze_stock(symbol)
        if data: results.append(data)
        time.sleep(0.5)
    
    output = {
        "last_updated": datetime.now(TW_TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "stocks": results
    }
    with open(DATA_FILE, "w", encoding='utf-8') as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
    return output

@app.route('/api/stocks')
def get_stocks():
    # 檢查快取
    if os.path.exists(DATA_FILE):
        file_age = time.time() - os.path.getmtime(DATA_FILE)
        if file_age < CACHE_SECONDS:
            print("Using cache...")
            with open(DATA_FILE, "r", encoding='utf-8') as f:
                return jsonify(json.load(f))
    
    # 過期或檔案不存在，抓新的
    print("Cache expired or missing, fetching new data...")
    data = update_cache()
    return jsonify(data)

if __name__ == "__main__":
    # 支援 Railway 動態分配的 Port
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)
