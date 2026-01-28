import yfinance as yf
import json
from datetime import datetime
import os
import time

def analyze_stock(symbol):
    print(f"Analyzing {symbol}...")
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # 基本數據
        name = info.get('shortName', symbol)
        summary = info.get('longBusinessSummary', '無公司介紹')
        price = info.get('currentPrice') or info.get('regularMarketPrice')
        prev_close = info.get('previousClose')
        
        # 變動率
        change = ((price - prev_close) / prev_close * 100) if price and prev_close else 0
        
        # 分析師數據
        target_price = info.get('targetMeanPrice')
        recommendation = info.get('recommendationKey', 'N/A').replace('_', ' ').title()
        analyst_count = info.get('numberOfAnalystOpinions', 0)
        
        # 外資/機構持股 (概略)
        inst_pct = info.get('heldPercentInstitutions', 0) * 100
        
        # 小U 評估邏輯
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
            "name": name,
            "price": price,
            "change": round(change, 2),
            "summary": summary[:150] + "...",
            "target_price": target_price,
            "recommendation": recommendation,
            "analyst_count": analyst_count,
            "inst_pct": round(inst_pct, 1),
            "evaluation": evaluation,
            "market": "台股" if symbol.endswith(".TW") else "美股"
        }
    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")
        return None

def fetch_all_stocks():
    # 定義觀察名單 (包含熱門與高波動)
    watchlist = [
        "NVDA", "TSLA", "MSTR", "AAPL", "AMD", "COIN", # 美股
        "2330.TW", "2317.TW", "2603.TW", "3231.TW", "2382.TW" # 台股
    ]
    
    results = []
    for symbol in watchlist:
        stock_data = analyze_stock(symbol)
        if stock_data:
            results.append(stock_data)
        time.sleep(1) # 避免請求過快
        
    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "stocks": results
    }
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(script_dir, "stock_data.json"), "w", encoding='utf-8') as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
    
    print(f"Successfully updated {len(results)} stocks in stock_data.json")

if __name__ == "__main__":
    fetch_all_stocks()
