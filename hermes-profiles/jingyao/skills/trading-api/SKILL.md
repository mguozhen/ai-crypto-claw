---
name: trading-api
description: Query the Trading Engine API for account status, trades, config, and grid management. Triggers on "balance", "status", "trades", "portfolio", "grid", "DCA".
version: 0.1.0
---

# Trading Engine API

Call the local Trading Engine to get real-time account data and manage grid trading.

## Endpoints

All endpoints are at `http://localhost:8000`.

### Read Operations
```bash
# User's account balance and positions
curl -s http://localhost:8000/api/status/2

# Recent trade history
curl -s http://localhost:8000/api/trades/2?limit=20

# Current strategy configuration
curl -s http://localhost:8000/api/config/2

# AI market analysis (GPT-5.4)
curl -s -X POST http://localhost:8000/api/analyze

# Command/operation logs
curl -s http://localhost:8000/api/commands?user_id=2
```

### Write Operations (use with care)
```bash
# Initialize grid orders (places real orders!)
curl -s -X POST http://localhost:8000/api/grid/init/2

# Stop all grid orders (cancels all open orders)
curl -s -X POST http://localhost:8000/api/grid/stop/2
```

## Response Format

All responses are JSON. Present key data in a readable format:
- Balance: show USDT, BTC, ETH amounts and total USD value
- Trades: show as a table with time, side, symbol, price, amount
- Config: summarize grid range, grid count, DCA amounts

## Notes
- Replace `2` with the user's numeric ID (check MEMORY.md for this)
- Grid init/stop are real operations — confirm with user before executing
- The Trading Engine runs independently; if it's down, tell the user
