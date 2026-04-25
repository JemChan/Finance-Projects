"""
Simple S&P 500 Top 10 Tracker
Run: pip install flask yfinance flask-cors  &&  python app.py
Then open: http://localhost:5000
"""

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import yfinance as yf
from datetime import datetime, timezone
import os

app = Flask(__name__, static_folder=".")
CORS(app)

# Top 10 S&P 500 by market cap
TOP_10 = [
    ("AAPL",  "Apple Inc."),
    ("MSFT",  "Microsoft Corp."),
    ("NVDA",  "NVIDIA Corp."),
    ("AMZN",  "Amazon.com Inc."),
    ("GOOGL", "Alphabet Inc."),
    ("META",  "Meta Platforms"),
    ("BRK-B", "Berkshire Hathaway"),
    ("LLY",   "Eli Lilly & Co."),
    ("AVGO",  "Broadcom Inc."),
    ("TSLA",  "Tesla Inc."),
]

SYMBOLS = [s for s, _ in TOP_10]
NAME_MAP = {s: n for s, n in TOP_10}


def safe_float(val):
    try:
        v = float(val)
        return None if (v != v) else round(v, 4)   # filter NaN
    except Exception:
        return None


@app.route("/api/quotes")
def quotes():
    try:
        tickers = yf.Tickers(" ".join(SYMBOLS))
        results = []

        for symbol in SYMBOLS:
            try:
                info = tickers.tickers[symbol].fast_info
                hist = tickers.tickers[symbol].history(period="2d", interval="1d")

                price      = safe_float(info.last_price)
                prev_close = safe_float(info.previous_close)
                day_high   = safe_float(info.day_high)
                day_low    = safe_float(info.day_low)
                mkt_cap    = safe_float(info.market_cap)
                volume     = safe_float(info.last_volume)

                change     = round(price - prev_close, 4) if price and prev_close else None
                change_pct = round((change / prev_close) * 100, 4) if change and prev_close else None

                # 5-day close prices for sparkline
                hist5 = tickers.tickers[symbol].history(period="5d", interval="1d")
                spark = [round(float(c), 2) for c in hist5["Close"].dropna().tolist()[-5:]]

                results.append({
                    "symbol":     symbol,
                    "name":       NAME_MAP.get(symbol, symbol),
                    "price":      price,
                    "change":     change,
                    "changePct":  change_pct,
                    "prevClose":  prev_close,
                    "dayHigh":    day_high,
                    "dayLow":     day_low,
                    "marketCap":  mkt_cap,
                    "volume":     volume,
                    "spark":      spark,
                })
            except Exception as e:
                results.append({
                    "symbol": symbol,
                    "name":   NAME_MAP.get(symbol, symbol),
                    "error":  str(e),
                })

        return jsonify({
            "data":      results,
            "fetchedAt": datetime.now(timezone.utc).isoformat(),
            "source":    "Yahoo Finance via yfinance"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n  S&P 500 Top 10 Tracker running at  http://localhost:{port}\n")
    app.run(debug=False, port=port)
