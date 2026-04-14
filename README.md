# AI-Crypto-Claw

A council of AI analysts for crypto research. Four specialist agents — **Technicals**, **Derivatives**, **TailRisk**, and a **PortfolioManager** — each read the same market data, form an opinion, and the PM aggregates their signals into per-asset decisions with evidence.

Pure Python. Stateless. No Hermes or FastAPI dependency — the engine is a library + CLI, usable from any host (Hermes skill, Telegram bot, backtest harness, notebook).

---

## Quick start

```bash
cd engine
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Offline demo (synthetic data — no network needed)
CRYPTO_CLAW_FAKE_DATA=1 python -m crypto_claw_engine analyze --universe BTC,ETH,SOL

# Live (requires un-geo-blocked access to Binance public REST)
python -m crypto_claw_engine analyze --universe BTC,ETH --json
```

## Architecture

```
           ┌────────────────┐
           │  PriceSource   │  CoinGecko / Binance (OHLCV)
           │  DerivSource   │  Binance futures (funding rate)
           └───────┬────────┘
                   │
           ┌───────▼────────┐
           │  Graph Runner  │  fetches data once, fans out to agents
           └───────┬────────┘
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
 ┌──────────┐ ┌──────────┐ ┌──────────┐
 │Technicals│ │Derivatives│ │ TailRisk │   Tier-A agents → Signals
 └─────┬────┘ └─────┬─────┘ └─────┬────┘
       └────────────┼─────────────┘
                    ▼
           ┌────────────────┐
           │PortfolioManager│  consensus → Decision (action, size, confidence)
           └────────────────┘
```

**Degrades gracefully:** any agent that fails returns a neutral-zero signal; the PM still produces a decision from whatever made it through. `agents_failed` in the result tells you who dropped.

## What's here

| Path | Purpose |
|---|---|
| `engine/crypto_claw_engine/` | Pydantic models, LLM protocol, data adapters, agents, graph runner, CLI |
| `engine/tests/` | 41 unit tests + 1 live golden-path integration test (marked `@pytest.mark.live`) |
| `engine/skills/crypto-claw/` | Hermes skill wrapper — drop into `~/.hermes/profiles/<p>/skills/research/` to expose the council over Telegram |
| `docs/superpowers/specs/` | Design spec (what we're building and why) |
| `docs/superpowers/plans/` | Implementation plan (task-by-task build) |

## Status

**M1 shipped** — skeleton, 4 agents, 2 data adapters, graph runner, CLI, Hermes skill. All 41 unit tests green.

Live golden-path blocked from the primary dev host (Binance returns HTTP 451 for geo-restricted regions). Test file is in place; run it from an un-blocked environment:

```bash
pytest engine/tests/test_live_golden_path.py -m live -v
```

**Next (M2):** parallel DAG execution, OKX adapter fallback, LLM-backed rationales (replace `FakeLLM`), position-sizing risk limits.

## Design principles

- **Stateless engine.** The runner takes a request and returns a result. No persistence, no background loops.
- **Evidence over opinion.** Every signal carries the numbers it was based on (`rsi`, `atr`, `funding_rate_mean`, `drawdown_30d`…). The PM's decision lists contributing signals verbatim.
- **Fake-data mode is a first-class path.** Offline demo, CI, and host-independent integration tests all share the same `CRYPTO_CLAW_FAKE_DATA=1` switch.

## License

TBD.
