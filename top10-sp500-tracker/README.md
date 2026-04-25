# S&P 500 Top 10 Tracker

A self-hosted real-time stock tracker for the top 10 S&P 500 companies.

## Setup

**Requirements:** Python 3.8+

### 1. Install dependencies

```bash
pip install flask yfinance flask-cors
```

### 2. Run the server

```bash
python app.py
```

### 3. Open in browser

```
http://localhost:5000
```

---

## What it shows

| Column     | Description                              |
|------------|------------------------------------------|
| Ticker     | Stock symbol                             |
| Company    | Full company name                        |
| Price      | Current market price (USD)               |
| Change     | Dollar change from previous close        |
| % Chg      | Percentage change from previous close    |
| Mkt Cap    | Total market capitalisation              |
| Volume     | Shares traded today                      |
| 5D         | 5-day price sparkline                    |
| Day Range  | Today's low → high with price dot        |

The dashboard auto-refreshes every **60 seconds**.
Click any column header to sort. Click **Refresh** to fetch immediately.

---

## Tracked stocks (top 10 S&P 500 by market cap)

1. AAPL  — Apple Inc.
2. MSFT  — Microsoft Corp.
3. NVDA  — NVIDIA Corp.
4. AMZN  — Amazon.com Inc.
5. GOOGL — Alphabet Inc.
6. META  — Meta Platforms
7. BRK-B — Berkshire Hathaway
8. LLY   — Eli Lilly & Co.
9. AVGO  — Broadcom Inc.
10. TSLA  — Tesla Inc.

---

## Data source

Data is fetched from **Yahoo Finance** via the `yfinance` Python library.
Quotes may be delayed 15–20 minutes during market hours.

---

## Changing the port

```bash
PORT=8080 python app.py
```
