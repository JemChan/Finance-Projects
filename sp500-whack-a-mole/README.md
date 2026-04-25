# S&P 500 Drop Tracker — Pro

A self-hosted trading dashboard tracking all 500 S&P 500 stocks in real time.

## Setup (same as before)

```bash
# 1. Install dependencies (only needed once)
pip3 install flask yfinance flask-cors

# 2. Start the server
python3 app.py

# 3. Open in browser — wait ~30-60s for first data load
open http://localhost:5000
```

---

## How it works

### Drop Columns (centre)
Three side-by-side columns show stocks that have dropped from their previous close:

| Column | Shows |
|--------|-------|
| −1%    | Stocks down between 1% and 2% |
| −2%    | Stocks down between 2% and Z% |
| −Z%    | Stocks down more than Z% |

**Z** is set by you in the top bar (default: 3%).

### Buying a Stock (left panel)
- Click any stock tile in the drop columns to **buy** it
- It moves to the **Buy List** on the left with your purchase price saved
- The Buy List has a maximum of **X** stocks (default: 10, set in top bar)

### Profit List (right panel)
- When a stock in your Buy List rises by **K%** above your buy price (default: 1%), it automatically moves to the **Profit List** on the right
- The Profit List shows:
  - Your buy price
  - Current price
  - % gain since buying
  - Dollar profit per share
- Click any stock in the Profit List to **sell** it (whack it!)

### Settings (top bar)
| Input | What it controls | Default |
|-------|-----------------|---------|
| Custom Drop % | The Z% threshold for column 3 | 3% |
| Max Holdings | Max stocks in your Buy List (X) | 10 |
| Profit Alert % | How much a stock must rise to appear in Profit List (K) | 1% |

---

## Data
- Source: **Yahoo Finance** via `yfinance`
- Refreshes every **60 seconds** automatically
- Portfolio is saved to `portfolio.json` — persists across restarts
- ~500 S&P 500 stocks tracked

---

## Stop the server
Press `Ctrl + C` in your terminal.
