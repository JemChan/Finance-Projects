"""
S&P 500 Whack-A-Mole: Full 500 Stock Trading Dashboard
Run: pip3 install flask yfinance flask-cors  &&  python3 app.py
Open: http://localhost:5000
"""

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import yfinance as yf
import json, os, time, threading
from datetime import datetime, timezone

app = Flask(__name__, static_folder=".")
CORS(app)

# ── ALL 500 S&P 500 SYMBOLS ──────────────────────────────────────
SP500 = [
    'AAPL','MSFT','NVDA','AMZN','GOOGL','META','BRK-B','LLY','AVGO','TSLA',
    'JPM','WMT','V','XOM','UNH','ORCL','MA','COST','HD','PG',
    'JNJ','NFLX','ABBV','BAC','CVX','MRK','KO','PM','CSCO','PEP',
    'TMO','AMD','ACN','CRM','ABT','MCD','ADBE','MS','GS','LIN',
    'QCOM','AXP','TXN','IBM','INTU','AMGN','CAT','GE','SPGI','DHR',
]
# Deduplicate while preserving order
seen = set()
SP500_CLEAN = []
for s in SP500:
    if s not in seen:
        seen.add(s)
        SP500_CLEAN.append(s)

PORTFOLIO_FILE = "portfolio.json"

# ── IN-MEMORY QUOTE CACHE ────────────────────────────────────────
cache = {"data": [], "fetched_at": None, "lock": threading.Lock()}

def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        try:
            with open(PORTFOLIO_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"holdings": [], "sold": []}

def save_portfolio(p):
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(p, f, indent=2)

def safe_float(v):
    try:
        f = float(v)
        return None if (f != f) else round(f, 4)
    except Exception:
        return None

def fetch_all_quotes():
    """Fetch all S&P 500 quotes in batches of 100."""
    results = []
    batch_size = 100
    symbols = SP500_CLEAN

    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i+batch_size]
        try:
            data = yf.download(
                batch,
                period="2d",
                interval="1d",
                group_by="ticker",
                auto_adjust=True,
                progress=False,
                threads=True,
            )
            info_batch = yf.Tickers(" ".join(batch))
            for sym in batch:
                try:
                    fi = info_batch.tickers[sym].fast_info
                    price      = safe_float(fi.last_price)
                    prev_close = safe_float(fi.previous_close)
                    day_high   = safe_float(fi.day_high)
                    day_low    = safe_float(fi.day_low)
                    mkt_cap    = safe_float(fi.market_cap)
                    volume     = safe_float(fi.last_volume)

                    change     = round(price - prev_close, 4) if price and prev_close else None
                    change_pct = round((change / prev_close) * 100, 4) if change and prev_close else None

                    # Short name
                    try:
                        name = info_batch.tickers[sym].info.get("shortName", sym)
                    except Exception:
                        name = sym

                    results.append({
                        "symbol":    sym,
                        "name":      name,
                        "price":     price,
                        "change":    change,
                        "changePct": change_pct,
                        "prevClose": prev_close,
                        "dayHigh":   day_high,
                        "dayLow":    day_low,
                        "marketCap": mkt_cap,
                        "volume":    volume,
                    })
                except Exception as e:
                    results.append({"symbol": sym, "name": sym, "error": str(e)})
        except Exception as e:
            for sym in batch:
                results.append({"symbol": sym, "name": sym, "error": str(e)})

    return results

def refresh_cache():
    """Background thread: refresh quotes every 60 seconds."""
    while True:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching all S&P 500 quotes…")
        data = fetch_all_quotes()
        with cache["lock"]:
            cache["data"] = data
            cache["fetched_at"] = datetime.now(timezone.utc).isoformat()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Done: {len(data)} stocks cached.")
        time.sleep(60)

# ── ROUTES ───────────────────────────────────────────────────────

@app.route("/api/quotes")
def api_quotes():
    with cache["lock"]:
        return jsonify({
            "data":      cache["data"],
            "fetchedAt": cache["fetched_at"],
            "count":     len(cache["data"]),
        })

@app.route("/api/portfolio", methods=["GET"])
def api_portfolio():
    return jsonify(load_portfolio())

@app.route("/api/buy", methods=["POST"])
def api_buy():
    body = request.get_json()
    symbol = body.get("symbol")
    price  = body.get("price")
    name   = body.get("name", symbol)

    if not symbol or price is None:
        return jsonify({"error": "symbol and price required"}), 400

    p = load_portfolio()

    # Check if already held
    if any(h["symbol"] == symbol for h in p["holdings"]):
        return jsonify({"error": "Already in portfolio"}), 409

    p["holdings"].append({
        "symbol":   symbol,
        "name":     name,
        "buyPrice": price,
        "boughtAt": datetime.now(timezone.utc).isoformat(),
    })
    save_portfolio(p)
    return jsonify({"ok": True, "holdings": p["holdings"]})

@app.route("/api/sell", methods=["POST"])
def api_sell():
    body        = request.get_json()
    symbol      = body.get("symbol")
    sell_price  = body.get("sellPrice")

    if not symbol:
        return jsonify({"error": "symbol required"}), 400

    p = load_portfolio()
    holding = next((h for h in p["holdings"] if h["symbol"] == symbol), None)
    if not holding:
        return jsonify({"error": "Not in portfolio"}), 404

    p["holdings"] = [h for h in p["holdings"] if h["symbol"] != symbol]
    profit_pct = round(((sell_price - holding["buyPrice"]) / holding["buyPrice"]) * 100, 2) \
                 if sell_price and holding["buyPrice"] else None
    profit_usd = round(sell_price - holding["buyPrice"], 4) \
                 if sell_price and holding["buyPrice"] else None
    p["sold"].append({
        **holding,
        "sellPrice": sell_price,
        "soldAt":    datetime.now(timezone.utc).isoformat(),
        "profitPct": profit_pct,
        "profitUsd": profit_usd,
    })
    save_portfolio(p)
    return jsonify({"ok": True, "holdings": p["holdings"], "sold": p["sold"]})

@app.route("/api/remove", methods=["POST"])
def api_remove():
    body   = request.get_json()
    symbol = body.get("symbol")
    if not symbol:
        return jsonify({"error": "symbol required"}), 400
    p = load_portfolio()
    p["holdings"] = [h for h in p["holdings"] if h["symbol"] != symbol]
    save_portfolio(p)
    return jsonify({"ok": True, "holdings": p["holdings"]})

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# ── STARTUP ──────────────────────────────────────────────────────
if __name__ == "__main__":
    t = threading.Thread(target=refresh_cache, daemon=True)
    t.start()
    port = int(os.environ.get("PORT", 5000))
    print(f"\n  S&P 500 Drop Tracker →  http://localhost:{port}\n")
    print("  First data load takes ~30s for all 500 stocks.\n")
    app.run(debug=False, port=port, use_reloader=False)
