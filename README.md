<p align="center">
  <img src="https://cdn-icons-png.flaticon.com/512/6003/6003226.png" width="80" alt="AI Crypto Claw">
</p>

<h1 align="center">AI-Crypto-Claw</h1>

<p align="center">
  <strong>AI-powered crypto trading system: multi-agent analysis + grid execution + Hermes Telegram copilot</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/agents-4%20analysts%20%2B%20PM-blue?style=flat-square" alt="4 Agents">
  <img src="https://img.shields.io/badge/exchange-OKX-FF9900?style=flat-square" alt="OKX">
  <img src="https://img.shields.io/badge/LLM-GPT--5.4-green?style=flat-square" alt="GPT-5.4">
  <img src="https://img.shields.io/badge/bot-Hermes%20Agent-8A2BE2?style=flat-square" alt="Hermes">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="MIT">
</p>

---

## Architecture

```
┌── Hermes Agent (per-user Telegram bot) ──────────┐
│  Free conversation + per-user memory + skills     │
│  "BTC行情怎么样?" → calls engine + trading API    │
└────────┬──────────────────────────┬───────────────┘
         │                          │
    ┌────▼─────┐              ┌────▼────────────┐
    │  Engine   │              │ Trading Engine   │
    │ (Analysis)│              │  (Execution)     │
    ├──────────┤              ├─────────────────┤
    │Technicals│              │ Grid Trading     │
    │Derivative│──decisions──▶│ DCA              │
    │ TailRisk │              │ Risk Management  │
    │    PM    │              │ GPT-5.4 Advisor  │
    └──────────┘              └─────────────────┘
```

## Three Components

### 1. Engine — AI Analyst Council (`engine/`)
4 specialist agents analyze crypto markets and produce consensus decisions:
- **Technicals Agent** — RSI, ATR, trend signals
- **Derivatives Agent** — funding rates, basis, open interest
- **TailRisk Agent** — drawdown, VaR, volatility regime
- **Portfolio Manager** — aggregates signals into long/short/flat decisions

```bash
cd engine && pip install -e "."
CRYPTO_CLAW_FAKE_DATA=1 python -m crypto_claw_engine analyze --universe BTC,ETH --json
```

### 2. Trading Engine — Grid + DCA Execution (`trading/`)
Automated trading on OKX with AI-powered risk management:
- **Grid Trading** — buy low, sell high within price range
- **DCA** — dollar cost average on schedule
- **GPT-5.4 Advisor** — market analysis every 15 min, pause on extreme risk
- **REST API** — all operations exposed as HTTP endpoints
- **Dashboard** — web UI for admin + user management

```bash
cd trading && pip install -r requirements.txt
python server.py  # API on :8000, Dashboard included
```

### 3. Hermes Profiles — Telegram Copilot (`hermes-profiles/`)
Each user gets their own Telegram bot with:
- **Free conversation** — ask anything about crypto, powered by LLM
- **Per-user memory** — remembers preferences, trading style, risk appetite
- **Self-evolution** — learns and creates reusable skills from conversations
- **Tool access** — calls Engine for analysis, Trading API for execution

```bash
hermes --profile jingyao  # Start user's bot
```

## Quick Start

### 1. Install
```bash
git clone https://github.com/mguozhen/ai-crypto-claw.git
cd ai-crypto-claw

# Engine
cd engine && python -m venv .venv && source .venv/bin/activate && pip install -e "."

# Trading
cd ../trading && pip install -r requirements.txt && cp .env.example .env
# Edit .env: add OKX keys, OPENROUTER_API_KEY, ENCRYPTION_KEY

# Hermes (if not already installed)
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### 2. Run
```bash
# Terminal 1: Trading Engine + Dashboard
cd trading && python server.py

# Terminal 2: User's Telegram bot
hermes --profile jingyao
```

### 3. Deploy (VPS)
```bash
bash deploy/setup.sh  # One-line VPS deployment
```

## Project Structure

```
ai-crypto-claw/
├── engine/                          # AI Analyst Council
│   ├── crypto_claw_engine/          # 4 agents + graph runner
│   ├── tests/                       # 41 unit tests
│   └── skills/crypto-claw/          # Hermes skill wrapper
├── trading/                         # Grid + DCA Execution
│   ├── server.py                    # FastAPI: API + Dashboard + Background tasks
│   ├── strategies/                  # grid.py, dca.py
│   ├── utils/                       # exchange, database, crypto, ai_advisor
│   └── templates/                   # Dashboard HTML
├── hermes-profiles/                 # Per-user Telegram bots
│   ├── template/                    # New user template
│   │   ├── SOUL.md                  # Agent role definition
│   │   └── skills/                  # trading-api, crypto-claw
│   └── jingyao/                     # First user (customized)
├── deploy/                          # VPS deployment scripts
└── docs/                            # Design specs + plans
```

## Adding a New User

1. Create Telegram bot via @BotFather → get token
2. Create user in Dashboard (`http://localhost:8000/admin/users/new`)
3. Copy profile: `cp -r hermes-profiles/template hermes-profiles/newuser`
4. Edit `SOUL.md`: replace `{USERNAME}` and `{USER_ID}`
5. Start: `hermes --profile newuser` → configure Telegram → paste bot token

## License

MIT
