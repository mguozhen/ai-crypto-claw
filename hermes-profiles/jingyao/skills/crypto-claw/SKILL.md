---
name: crypto-claw
description: Run the AI-Crypto-Claw council (Technicals + Derivatives + TailRisk + PortfolioManager) against a crypto universe and return decisions with evidence. Triggers on "analyze BTC", "crypto claw", "run council on X,Y", "what does claw say about SOL".
version: 0.1.0
metadata:
  hermes:
    tags: [crypto, trading, research, analysis]
    related_skills: []
---

# Crypto-Claw Council

Invoke the local AI-Crypto-Claw engine to analyze a crypto universe. The engine fans out to four agents (Technicals, Derivatives, TailRisk, PortfolioManager) and returns per-asset decisions with evidence.

## When to use

Trigger on requests like:
- "analyze BTC ETH"
- "run crypto claw on SOL,AVAX"
- "what does the council say about BTC?"
- "crypto analysis for <ticker(s)>"

## Invocation

Always call the CLI. Do NOT reimplement logic — the engine is the source of truth.

**Working directory:** `/Users/guozhen/AI-Crypto-Claw/engine`
**Python interpreter:** `/Users/guozhen/AI-Crypto-Claw/engine/.venv/bin/python`

### Command

```bash
cd /Users/guozhen/AI-Crypto-Claw/engine && \
  CRYPTO_CLAW_FAKE_DATA=${FAKE:-0} \
  .venv/bin/python -m crypto_claw_engine analyze \
    --universe <TICKERS> --json
```

- `<TICKERS>` — comma-separated, uppercase (e.g. `BTC,ETH,SOL`). Extract from user message.
- `--json` — always pass so you get machine-readable output.
- Set env `FAKE=1` if the user says "demo", "fake data", "offline", or Binance is known to be geo-blocked from this host (HTTP 451). Otherwise leave live.

### Parsing output

The last line of stdout is JSON with this shape:

```json
{
  "run_id": "...",
  "as_of": "...",
  "decisions": [
    {"asset": "BTC", "action": "long|short|flat", "size_pct": 0.12, "confidence": 0.6,
     "reasoning": "...", "contributing_signals": [{"agent":"technicals","stance":"bullish","confidence":0.5,"rationale":"..."}]}
  ],
  "signals": [...],
  "agents_failed": []
}
```

## Response format

Present to user as a compact table + one-line evidence per asset:

```
<ASSET>: <ACTION> size=<±X%> conf=<Y>
  tech: <stance> (<conf>) — <rationale first clause>
  deriv: <stance> (<conf>) — <...>
  tail:  <stance> (<conf>) — <...>
```

Then one line: `run <run_id> @ <as_of>`. If `agents_failed` non-empty, flag it.

## Notes

- This is research output, not financial advice — always append a one-line disclaimer.
- If Binance returns 451 (US/geo-blocked), retry with `FAKE=1` and tell the user the run used synthetic data.
- Do not loop or re-run automatically; one call per request.
