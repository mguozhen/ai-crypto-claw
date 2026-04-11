# AI-Crypto-Claw — Design Spec

**Date:** 2026-04-11
**Author:** MailOutreachAgent + Bo Yuan (via brainstorming session)
**Status:** Approved (pending user review of this doc)
**Today's execution scope:** Tier 1 — engine only (see §6)

## 1. Goal

Build a crypto-first "council of AI analysts" system that consumes a universe of crypto assets and returns structured buy/sell/hold decisions with per-agent rationale, usable by quant traders.

**Inspiration:** [ai-hedge-fund](https://github.com/virattt/ai-hedge-fund) (19 investor-persona agents for US equities).
**Host:** Integrates into [hermes-agent](https://github.com/NousResearch/hermes-agent) ("龙虾") as a skill.
**Users:** 10-50 trusted quant friends (closed beta), email magic-link auth, no billing, no SaaS surface.
**Mobile:** Telegram bot via Hermes gateway (no native app).
**Dev workflow:** [gstack](https://github.com/garrytan/gstack) slash commands for product/code review (not a runtime component).

## 2. Non-Goals

- Real trade execution. Signals only. No broker/exchange API writes in v0.
- US equity support. Crypto only. Fundamental-persona agents (Buffett/Graham/Munger/...) are dropped, not ported.
- Intraday HFT. Default horizon is daily; intraday is a flag for a small subset of agents.
- Public SaaS. Closed beta with hardcoded email allowlist.
- Perfect LLM answer correctness. We validate pipeline plumbing and evidence traceability, not model outputs.

## 3. Architecture

Three components, one shared engine.

```
crypto_claw_engine/           ← pure Python package, stateless
  agents/                     ← 10 crypto analyst agents
  data/                       ← adapters: CoinGecko, Binance, DeFiLlama, Coinglass, CryptoPanic, alternative.me
  graph/                      ← LangGraph orchestration
  backtest/                   ← historical replay + equity curve
  models.py                   ← pydantic schemas (RunRequest, AgentSignal, Decision, ...)
  llm.py                      ← LLMClient Protocol (injected by shell)

hermes-agent/skills/finance/crypto-claw/   ← Shell A: Hermes skill
  SKILL.md                    ← skill metadata
  scripts/                    ← thin entry points: analyze, watch (cron), backtest, alerts
  references/                 ← agent roster + data source cheat sheet
  config.example.yaml
  # engine installed via `pip install -e <path>` into Hermes venv

AI-Crypto-Claw/app/           ← Shell B: Web app
  backend/                    ← FastAPI + SQLAlchemy + Alembic
    routes/                   ← /api/runs, /api/signals, /api/backtest, /api/portfolio, /auth/*
    services/                 ← engine_runner, telegram_push, cache
    db/                       ← models, migrations
  frontend/                   ← Vite + React + Tailwind (adapted from ai-hedge-fund frontend)
    pages/                    ← Dashboard, RunDetail, Backtest, Portfolio, Settings, Login
```

### Key architectural rules

1. **Engine is host-agnostic.** It does not know about Hermes or FastAPI. It accepts a `RunRequest` and returns a `RunResult`. LLM is dependency-injected.
2. **Engine is stateless.** Persistence is the shell's responsibility.
3. **One engine execution path.** The web backend is the sole caller of `engine.run()`. Hermes skill becomes a client that POSTs to the backend. Single source of truth for history; no version drift between surfaces.
4. **Monorepo for app + engine + spec.** Hermes skill stays in `hermes-agent` repo and references the engine via pip install path.

## 4. Agent Roster (10 agents)

| # | Agent | Origin | Role | Primary data |
|---|---|---|---|---|
| 1 | TechnicalsAgent | ported from ai-hedge-fund | RSI/MACD/Bollinger/ATR/SuperTrend/volume profile | OHLCV |
| 2 | OnChainFlowAgent | new | exchange netflows, whale transfers, stablecoin supply | Glassnode free tier, on-chain scrapers |
| 3 | DeFiAgent | new | protocol TVL changes, DEX volume, yield curves | DeFiLlama |
| 4 | DerivativesAgent | new | funding rates, open interest, perp basis, liquidations | Binance public REST, Coinglass |
| 5 | SentimentAgent | ported | news sentiment + X mentions + Fear & Greed | CryptoPanic, alternative.me |
| 6 | NarrativeAgent | new | rotating narrative tracker (AI, RWA, DePIN, meme, L2) | CoinGecko categories + LLM synthesis |
| 7 | MacroAgent | ported from Druckenmiller | DXY, BTC dominance, stablecoin supply, global M2 | public macro APIs + CoinGecko |
| 8 | TailRiskAgent | Taleb preserved | volatility regime, drawdown, asymmetric hedge flags | OHLCV + derivatives |
| 9 | RiskManager | ported, adapted | position sizing, correlation caps, concentration limits | outputs of agents 1-8 |
| 10 | PortfolioManager | ported, adapted | final decision synthesis | all above + current portfolio |

**Dropped from ai-hedge-fund:** Buffett, Graham, Munger, Damodaran, Fisher, Lynch, Pabrai, Burry, Ackman, Fundamentals, Valuation. All require DCF, P/E, book value, moats, or dividend analysis — not meaningful for crypto. Forcing them would produce fabricated LLM output.

**Kept personality:** Taleb (TailRisk) is the only persona-branded agent that survives. Asymmetric payoffs and tail risk apply more to crypto than equities.

## 5. Data Contracts

```python
class RunRequest(BaseModel):
    universe: list[str]                                    # e.g. ["BTC", "ETH", "SOL"]
    horizon: Literal["intraday", "daily", "weekly"] = "daily"
    as_of: datetime | None = None                          # None = now; set for backtests
    portfolio: Portfolio                                   # current holdings + cash
    agents_enabled: list[str] | None = None                # None = all 10
    llm_model_tier: Literal["cheap", "mid", "best"] | None = None

class AgentSignal(BaseModel):
    agent: str                                             # "technicals"
    asset: str                                             # "BTC"
    stance: Literal["bullish", "bearish", "neutral"]
    confidence: float                                      # 0.0 to 1.0
    rationale: str                                         # natural-language LLM output
    evidence: dict                                         # structured datapoints used

class Decision(BaseModel):
    asset: str
    action: Literal["buy", "sell", "hold", "close"]
    size_pct: float                                        # suggested allocation %
    confidence: float
    reasoning: str                                         # PM's synthesis
    contributing_signals: list[AgentSignal]
    risk_notes: str                                        # from RiskManager

class RunResult(BaseModel):
    run_id: str
    as_of: datetime
    signals: list[AgentSignal]
    decisions: list[Decision]
    cost_usd: float
    agents_failed: list[str]
```

These schemas are the stable engine API. Both shells consume the same pydantic objects.

## 6. Execution Scope — Today (Tier 1)

Full design above is the north star. Today we ship only the engine foundation:

**In scope today:**
- `crypto_claw_engine` package skeleton
- Pydantic schemas (models.py) exactly as defined in §5
- LLM `Protocol` in llm.py + a fake LLM for tests
- Data adapters: **CoinGecko** (prices, categories), **Binance public REST** (OHLCV, funding, OI)
- 4 agents: **TechnicalsAgent, DerivativesAgent, TailRiskAgent, PortfolioManager**
- LangGraph orchestration wiring Tier-A agents (Technicals + Derivatives + TailRisk) in parallel, then PM
- CLI entry point: `python -m crypto_claw_engine analyze --universe BTC,ETH,SOL [--portfolio-file path.json] [--horizon daily] [--as-of 2026-04-11]` prints structured JSON + human-readable summary. If `--portfolio-file` is omitted, CLI defaults to an empty portfolio with $10,000 cash for demo purposes.
- Unit tests: every adapter (with recorded fixtures), every agent (fake LLM), engine smoke test
- One golden-path integration test that actually hits CoinGecko + Binance and asserts the pipeline produces decisions

**Deferred (not today):**
- Agents: OnChain, DeFi, Sentiment, Narrative, Macro, RiskManager (placeholder stubs that return `neutral` + note "not yet implemented")
- Web backend, frontend, auth, DB, Alembic, Telegram push
- Backtest engine
- Hermes skill shell
- Docker, VPS, deployment
- Caching layer (today's adapters hit APIs directly; caching is v0.2)

**Done today = these 3 things verified:**
1. `pytest` green on unit + integration
2. `python -m crypto_claw_engine analyze --universe BTC,ETH --horizon daily` runs against live CoinGecko + Binance and prints real decisions with real rationale
3. Git committed to `/Users/guozhen/AI-Crypto-Claw`

## 7. Error Handling

Three-layer degradation:

| Failure | Response |
|---|---|
| Data source timeout/error | Adapter raises `DataGap`; agent receives empty data and emits `stance=neutral, confidence=0, rationale="data unavailable"`. Run continues. |
| Single-agent LLM failure | Retry once; on second failure mark agent `failed`; PM continues with available agents but scales final confidence by `len(available) / len(enabled)`. |
| PortfolioManager failure | Mark run `failed`. No Decision emitted. Raise structured error to caller. |

**Absolute rules:** never silently fabricate data, never reuse a previous run's output to mask a current failure, every evidence field must trace back to a real API response or be explicitly marked null.

## 8. Cost Control (deferred to v0.2 but designed in now)

LLM model tier routing baked into engine (via `llm_model_tier` param and per-agent default):

- **cheap** (Haiku / gpt-4o-mini / DeepSeek): Technicals, Derivatives, OnChain — data-heavy, reasoning-light
- **mid** (Sonnet / gpt-4o): Sentiment, Narrative, Macro, TailRisk — synthesis-heavy
- **best** (Opus / top-tier): RiskManager, PortfolioManager — consequential decisions

Hard per-run budget (default $0.50) and prompt-hash LLM cache are v0.2 (not today).

## 9. Testing Strategy

| Layer | Approach |
|---|---|
| engine unit | Per-agent + per-adapter with recorded JSON fixtures |
| engine integration | `pytest-recording` cassettes; replay real API responses |
| engine smoke | Fake LLM, one asset, one agent, <2s, runs every commit |
| (deferred) backend API | FastAPI TestClient, engine swapped for fake |
| (deferred) frontend | Playwright golden path |
| manual | One live `analyze BTC,ETH` after each commit; eyeball decisions |

**Not doing:** LLM output correctness snapshots (unstable), load/stress testing (irrelevant for 50 users).

## 10. Rollout Milestones (post-today)

| M | Scope | Estimate |
|---|---|---|
| M1 (today) | Engine skeleton + 4 agents + 2 data sources + CLI | ~1 day |
| M2 | Remaining 6 agents + 4 data sources + LangGraph full DAG | 3-4 days |
| M3 | Backend (FastAPI + SQLite + engine_runner + auth stub) | 2-3 days |
| M4 | Frontend (Dashboard, RunDetail, Portfolio) | 3-4 days |
| M5 | Hermes skill shell + cron + Telegram push | 2 days |
| M6 | Backtest + equity curve + deployment via docker-compose | 3-4 days |

Each milestone ends with a gstack `/review` pass before moving on. Spec-level review (`/plan-ceo-review`) happens before M1 starts.

## 11. Open Questions / Known Unknowns

- **LLM cost at scale**: we have not measured a full 10-agent, 20-asset run cost. Do it once M3 completes and reality-check the $0.50 budget.
- **Data source quality for mid-cap alts**: Binance public REST covers majors cleanly but may gap on newer tokens. If the universe includes anything beyond top-30, verify adapter coverage per asset.
- **Hermes plugin vs skill**: `hermes-agent` has both `plugins/` and `skills/` — we chose skill based on polymarket precedent, but plugin may be the right layer if the engine needs lifecycle hooks. Re-evaluate at M5.
- **Portfolio data source**: MVP reads `~/.crypto-claw/portfolio.json`. Eventually tie to exchange read-only API keys. Not today.

## 12. Glossary

- **Council**: the set of 10 agents collectively analyzing the universe for one `RunRequest`.
- **Universe**: the list of assets being analyzed in a single run.
- **Tier A/B/C**: parallelism tier inside LangGraph. Tier A = data-driven agents (parallel), Tier B = RiskManager (reads Tier A), Tier C = PortfolioManager (reads B).
- **Evidence**: the structured datapoints an agent used, stored on every signal for audit.
- **Shell**: a thin layer (Hermes skill or FastAPI backend) that drives the engine and handles persistence/UX.
