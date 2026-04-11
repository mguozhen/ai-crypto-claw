# AI-Crypto-Claw M1 — Engine Skeleton Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a working `crypto_claw_engine` Python package with 4 crypto analyst agents (Technicals, Derivatives, TailRisk, PortfolioManager), 2 data adapters (CoinGecko, Binance public REST), a LangGraph orchestration layer, and a CLI that runs `analyze --universe BTC,ETH,SOL` end-to-end against fake LLM, plus one live golden-path integration test.

**Architecture:** Pure Python package, dependency-injected LLM (Protocol), stateless engine. Data adapters raise `DataGap` on failure; agents degrade gracefully. LangGraph runs Tier-A agents (Technicals, Derivatives, TailRisk) in parallel, then PortfolioManager. CLI uses `FakeLLM` today; real LLM client is hooked up in M3+ when shells are built.

**Tech Stack:** Python 3.11+, pydantic v2, httpx, pandas, ta (technical indicators), langgraph, click, pytest. No langchain-core LLM lock-in.

**Spec reference:** `/Users/guozhen/AI-Crypto-Claw/docs/superpowers/specs/2026-04-11-ai-crypto-claw-design.md` — this plan implements §6 only.

---

## File Structure

```
AI-Crypto-Claw/
├── engine/
│   ├── pyproject.toml
│   ├── README.md
│   ├── crypto_claw_engine/
│   │   ├── __init__.py
│   │   ├── __main__.py              # python -m crypto_claw_engine
│   │   ├── models.py                # pydantic schemas
│   │   ├── llm.py                   # LLMClient Protocol + FakeLLM
│   │   ├── errors.py                # DataGap, EngineError
│   │   ├── data/
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # PriceSource, DerivSource Protocols
│   │   │   ├── coingecko.py         # CoinGeckoAdapter
│   │   │   └── binance.py           # BinanceAdapter
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # AgentBase
│   │   │   ├── technicals.py        # TechnicalsAgent
│   │   │   ├── derivatives.py       # DerivativesAgent
│   │   │   ├── tail_risk.py         # TailRiskAgent
│   │   │   └── portfolio_manager.py # PortfolioManagerAgent
│   │   ├── graph/
│   │   │   ├── __init__.py
│   │   │   └── runner.py            # build_graph, run()
│   │   └── cli.py                   # click CLI
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py              # shared fixtures
│       ├── fixtures/
│       │   ├── coingecko_simple_price.json
│       │   ├── coingecko_markets.json
│       │   ├── binance_klines_btc.json
│       │   ├── binance_funding_btc.json
│       │   └── binance_oi_btc.json
│       ├── test_models.py
│       ├── test_llm.py
│       ├── test_data_coingecko.py
│       ├── test_data_binance.py
│       ├── test_agent_technicals.py
│       ├── test_agent_derivatives.py
│       ├── test_agent_tail_risk.py
│       ├── test_agent_portfolio_manager.py
│       ├── test_graph_runner.py
│       ├── test_cli.py
│       └── test_live_golden_path.py  # hits real APIs, marked @pytest.mark.live
```

Each file has a single responsibility. Nothing imports LangGraph except `graph/runner.py`. Nothing imports httpx except `data/*.py`. Agents never import data adapters — they receive pre-fetched data via the runner.

---

## Task 1: Project Skeleton

**Files:**
- Create: `engine/pyproject.toml`
- Create: `engine/README.md`
- Create: `engine/crypto_claw_engine/__init__.py`
- Create: `engine/tests/__init__.py`
- Create: `engine/tests/conftest.py`
- Create: `engine/tests/test_smoke.py`

- [ ] **Step 1: Create pyproject.toml**

Create `engine/pyproject.toml`:

```toml
[project]
name = "crypto-claw-engine"
version = "0.1.0"
description = "Crypto-first council of AI analysts — engine package"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.7",
    "httpx>=0.27",
    "pandas>=2.2",
    "numpy>=1.26",
    "ta>=0.11",
    "langgraph>=0.2",
    "click>=8.1",
    "python-dotenv>=1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "respx>=0.21",
]

[project.scripts]
crypto-claw = "crypto_claw_engine.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["crypto_claw_engine"]

[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "live: hits real external APIs (requires network)",
]
```

- [ ] **Step 2: Create README stub**

Create `engine/README.md`:

```markdown
# crypto-claw-engine

Pure Python engine for AI-Crypto-Claw. Stateless. No Hermes or FastAPI dependency. See `../docs/superpowers/specs/2026-04-11-ai-crypto-claw-design.md`.

## Install (editable)

    cd engine && pip install -e ".[dev]"

## Run

    python -m crypto_claw_engine analyze --universe BTC,ETH,SOL

## Test

    pytest                    # unit tests only
    pytest -m live            # hit real CoinGecko + Binance
```

- [ ] **Step 3: Create empty package**

Create `engine/crypto_claw_engine/__init__.py`:

```python
"""crypto_claw_engine — AI council of crypto analysts (engine layer)."""

__version__ = "0.1.0"
```

Create `engine/tests/__init__.py` as an empty file.

- [ ] **Step 4: Create conftest and smoke test**

Create `engine/tests/conftest.py`:

```python
import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def load_fixture():
    def _load(name: str) -> dict | list:
        return json.loads((FIXTURES / name).read_text())
    return _load
```

Create `engine/tests/test_smoke.py`:

```python
def test_package_imports():
    import crypto_claw_engine
    assert crypto_claw_engine.__version__ == "0.1.0"
```

- [ ] **Step 5: Install and run smoke test**

Run:

```bash
cd /Users/guozhen/AI-Crypto-Claw/engine
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]" -q
pytest tests/test_smoke.py -v
```

Expected: `1 passed`.

- [ ] **Step 6: Commit**

```bash
cd /Users/guozhen/AI-Crypto-Claw
git add engine/pyproject.toml engine/README.md engine/crypto_claw_engine/ engine/tests/
echo ".venv/" > engine/.gitignore
echo "__pycache__/" >> engine/.gitignore
echo "*.egg-info/" >> engine/.gitignore
git add engine/.gitignore
git commit -m "feat(engine): project skeleton with smoke test"
```

---

## Task 2: Pydantic Schemas

**Files:**
- Create: `engine/crypto_claw_engine/models.py`
- Create: `engine/crypto_claw_engine/errors.py`
- Create: `engine/tests/test_models.py`

- [ ] **Step 1: Write failing test**

Create `engine/tests/test_models.py`:

```python
from datetime import datetime

import pytest
from pydantic import ValidationError

from crypto_claw_engine.models import (
    AgentSignal,
    Decision,
    Portfolio,
    RunRequest,
    RunResult,
)


def test_portfolio_construction():
    p = Portfolio(cash_usd=10_000.0, holdings={"BTC": 0.1})
    assert p.cash_usd == 10_000.0
    assert p.holdings["BTC"] == 0.1


def test_run_request_defaults():
    req = RunRequest(universe=["BTC", "ETH"], portfolio=Portfolio(cash_usd=1000))
    assert req.horizon == "daily"
    assert req.as_of is None
    assert req.agents_enabled is None


def test_agent_signal_stance_validation():
    AgentSignal(
        agent="technicals",
        asset="BTC",
        stance="bullish",
        confidence=0.75,
        rationale="RSI 28, MACD turning up",
        evidence={"rsi": 28.0},
    )
    with pytest.raises(ValidationError):
        AgentSignal(
            agent="technicals",
            asset="BTC",
            stance="confused",  # invalid
            confidence=0.5,
            rationale="x",
            evidence={},
        )


def test_agent_signal_confidence_bounds():
    with pytest.raises(ValidationError):
        AgentSignal(
            agent="x",
            asset="BTC",
            stance="neutral",
            confidence=1.5,  # out of range
            rationale="x",
            evidence={},
        )


def test_decision_fields():
    d = Decision(
        asset="BTC",
        action="buy",
        size_pct=0.1,
        confidence=0.7,
        reasoning="Consensus bullish across technicals and derivatives.",
        contributing_signals=[],
        risk_notes="",
    )
    assert d.action == "buy"
    assert d.size_pct == 0.1


def test_run_result_fields():
    r = RunResult(
        run_id="abc",
        as_of=datetime(2026, 4, 11),
        signals=[],
        decisions=[],
        cost_usd=0.0,
        agents_failed=[],
    )
    assert r.run_id == "abc"
```

- [ ] **Step 2: Run test, expect ImportError**

Run:

```bash
pytest tests/test_models.py -v
```

Expected: all fail with `ImportError: cannot import name 'AgentSignal' from 'crypto_claw_engine.models'`.

- [ ] **Step 3: Create errors.py**

Create `engine/crypto_claw_engine/errors.py`:

```python
class EngineError(Exception):
    """Base class for engine errors."""


class DataGap(EngineError):
    """Raised when a data source cannot supply required data for an agent."""

    def __init__(self, source: str, key: str, reason: str = ""):
        self.source = source
        self.key = key
        self.reason = reason
        super().__init__(f"data gap: {source}/{key} ({reason})")


class AgentFailure(EngineError):
    """Raised when an agent fails after retries."""
```

- [ ] **Step 4: Create models.py**

Create `engine/crypto_claw_engine/models.py`:

```python
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Stance = Literal["bullish", "bearish", "neutral"]
Action = Literal["buy", "sell", "hold", "close"]
Horizon = Literal["intraday", "daily", "weekly"]
ModelTier = Literal["cheap", "mid", "best"]


class Portfolio(BaseModel):
    cash_usd: float = 0.0
    holdings: dict[str, float] = Field(default_factory=dict)  # symbol -> units


class RunRequest(BaseModel):
    universe: list[str]
    horizon: Horizon = "daily"
    as_of: datetime | None = None
    portfolio: Portfolio = Field(default_factory=Portfolio)
    agents_enabled: list[str] | None = None
    llm_model_tier: ModelTier | None = None


class AgentSignal(BaseModel):
    agent: str
    asset: str
    stance: Stance
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str
    evidence: dict


class Decision(BaseModel):
    asset: str
    action: Action
    size_pct: float = Field(ge=-1.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    contributing_signals: list[AgentSignal] = Field(default_factory=list)
    risk_notes: str = ""


class RunResult(BaseModel):
    run_id: str
    as_of: datetime
    signals: list[AgentSignal]
    decisions: list[Decision]
    cost_usd: float = 0.0
    agents_failed: list[str] = Field(default_factory=list)
```

- [ ] **Step 5: Run tests, expect pass**

Run:

```bash
pytest tests/test_models.py -v
```

Expected: `6 passed`.

- [ ] **Step 6: Commit**

```bash
git add engine/crypto_claw_engine/models.py engine/crypto_claw_engine/errors.py engine/tests/test_models.py
git commit -m "feat(engine): pydantic schemas and error types"
```

---

## Task 3: LLM Protocol + FakeLLM

**Files:**
- Create: `engine/crypto_claw_engine/llm.py`
- Create: `engine/tests/test_llm.py`

- [ ] **Step 1: Write failing test**

Create `engine/tests/test_llm.py`:

```python
from crypto_claw_engine.llm import FakeLLM, LLMClient


def test_fake_llm_returns_canned_response():
    llm = FakeLLM({"technicals": "Scripted technicals rationale"})
    out = llm.complete(
        messages=[{"role": "user", "content": "anything"}],
        tag="technicals",
    )
    assert out == "Scripted technicals rationale"


def test_fake_llm_default_fallback():
    llm = FakeLLM()
    out = llm.complete(
        messages=[{"role": "user", "content": "anything"}],
        tag="unknown-agent",
    )
    assert "fake" in out.lower()


def test_fake_llm_records_calls():
    llm = FakeLLM()
    llm.complete(messages=[{"role": "user", "content": "hi"}], tag="x")
    llm.complete(messages=[{"role": "user", "content": "hi"}], tag="y")
    assert len(llm.calls) == 2
    assert llm.calls[0]["tag"] == "x"


def test_llm_client_protocol_shape():
    # Protocol check: FakeLLM must satisfy LLMClient at type level.
    llm: LLMClient = FakeLLM()
    assert hasattr(llm, "complete")
```

- [ ] **Step 2: Run test, expect fail**

Run:

```bash
pytest tests/test_llm.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement llm.py**

Create `engine/crypto_claw_engine/llm.py`:

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMClient(Protocol):
    def complete(
        self,
        messages: list[dict],
        *,
        tag: str = "",
        model: str | None = None,
    ) -> str:
        ...


class FakeLLM:
    """Deterministic LLM used in tests and the today-only CLI default.

    Returns a scripted rationale keyed by `tag` (agent name). Falls back to a
    generic sentence that includes the tag so agents can still produce human-
    readable output without any API cost.
    """

    def __init__(self, scripts: dict[str, str] | None = None):
        self.scripts = scripts or {}
        self.calls: list[dict] = []

    def complete(
        self,
        messages: list[dict],
        *,
        tag: str = "",
        model: str | None = None,
    ) -> str:
        self.calls.append({"messages": messages, "tag": tag, "model": model})
        if tag in self.scripts:
            return self.scripts[tag]
        return f"[fake-llm:{tag or 'default'}] synthesized rationale based on evidence."
```

- [ ] **Step 4: Run tests, expect pass**

Run:

```bash
pytest tests/test_llm.py -v
```

Expected: `4 passed`.

- [ ] **Step 5: Commit**

```bash
git add engine/crypto_claw_engine/llm.py engine/tests/test_llm.py
git commit -m "feat(engine): LLMClient protocol and FakeLLM"
```

---

## Task 4: Data Source Protocols

**Files:**
- Create: `engine/crypto_claw_engine/data/__init__.py`
- Create: `engine/crypto_claw_engine/data/base.py`
- Create: `engine/tests/test_data_base.py`

- [ ] **Step 1: Write failing test**

Create `engine/tests/test_data_base.py`:

```python
from datetime import datetime, timezone

from crypto_claw_engine.data.base import (
    DerivSnapshot,
    OHLCVBar,
    PriceSnapshot,
)


def test_price_snapshot_fields():
    s = PriceSnapshot(symbol="BTC", price_usd=65000.0, market_cap_usd=1.3e12, volume_24h_usd=3.5e10)
    assert s.symbol == "BTC"


def test_ohlcv_bar_fields():
    bar = OHLCVBar(
        open_time=datetime(2026, 4, 10, tzinfo=timezone.utc),
        open=64000,
        high=65500,
        low=63800,
        close=65000,
        volume=12345.6,
    )
    assert bar.close == 65000


def test_deriv_snapshot_fields():
    d = DerivSnapshot(
        symbol="BTCUSDT",
        funding_rate=0.0001,
        open_interest_usd=1.2e10,
        as_of=datetime(2026, 4, 10, tzinfo=timezone.utc),
    )
    assert d.funding_rate == 0.0001
```

- [ ] **Step 2: Run, expect fail**

Run:

```bash
pytest tests/test_data_base.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Create base.py**

Create `engine/crypto_claw_engine/data/__init__.py` as an empty file.

Create `engine/crypto_claw_engine/data/base.py`:

```python
from datetime import datetime
from typing import Protocol

from pydantic import BaseModel


class PriceSnapshot(BaseModel):
    symbol: str
    price_usd: float
    market_cap_usd: float | None = None
    volume_24h_usd: float | None = None


class OHLCVBar(BaseModel):
    open_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class DerivSnapshot(BaseModel):
    symbol: str
    funding_rate: float
    open_interest_usd: float | None = None
    as_of: datetime


class PriceSource(Protocol):
    def get_price(self, symbol: str) -> PriceSnapshot: ...
    def get_ohlcv(self, symbol: str, interval: str, limit: int) -> list[OHLCVBar]: ...


class DerivSource(Protocol):
    def get_funding(self, symbol: str, limit: int) -> list[DerivSnapshot]: ...
    def get_open_interest(self, symbol: str) -> DerivSnapshot: ...
```

- [ ] **Step 4: Run tests, expect pass**

Run:

```bash
pytest tests/test_data_base.py -v
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
git add engine/crypto_claw_engine/data/ engine/tests/test_data_base.py
git commit -m "feat(engine): data source protocols and domain types"
```

---

## Task 5: CoinGecko Adapter

**Files:**
- Create: `engine/tests/fixtures/coingecko_simple_price.json`
- Create: `engine/tests/fixtures/coingecko_markets.json`
- Create: `engine/crypto_claw_engine/data/coingecko.py`
- Create: `engine/tests/test_data_coingecko.py`

- [ ] **Step 1: Create fixture files**

Create `engine/tests/fixtures/coingecko_simple_price.json`:

```json
{
  "bitcoin": {"usd": 65000.0, "usd_market_cap": 1280000000000.0, "usd_24h_vol": 35000000000.0},
  "ethereum": {"usd": 3400.0, "usd_market_cap": 410000000000.0, "usd_24h_vol": 18000000000.0}
}
```

Create `engine/tests/fixtures/coingecko_markets.json`:

```json
[
  {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "current_price": 65000.0, "market_cap": 1280000000000.0, "total_volume": 35000000000.0},
  {"id": "ethereum", "symbol": "eth", "name": "Ethereum", "current_price": 3400.0, "market_cap": 410000000000.0, "total_volume": 18000000000.0}
]
```

- [ ] **Step 2: Write failing test**

Create `engine/tests/test_data_coingecko.py`:

```python
import httpx
import pytest
import respx

from crypto_claw_engine.data.coingecko import CoinGeckoAdapter
from crypto_claw_engine.errors import DataGap


def test_get_price_known_symbol(load_fixture):
    with respx.mock(base_url="https://api.coingecko.com/api/v3") as mock:
        mock.get("/simple/price").mock(
            return_value=httpx.Response(200, json=load_fixture("coingecko_simple_price.json"))
        )
        adapter = CoinGeckoAdapter()
        snap = adapter.get_price("BTC")
        assert snap.symbol == "BTC"
        assert snap.price_usd == 65000.0
        assert snap.market_cap_usd == 1280000000000.0


def test_get_price_unknown_symbol_raises_data_gap():
    with respx.mock(base_url="https://api.coingecko.com/api/v3") as mock:
        mock.get("/simple/price").mock(return_value=httpx.Response(200, json={}))
        adapter = CoinGeckoAdapter()
        with pytest.raises(DataGap) as exc:
            adapter.get_price("BTC")
        assert exc.value.source == "coingecko"


def test_get_price_http_error_raises_data_gap():
    with respx.mock(base_url="https://api.coingecko.com/api/v3") as mock:
        mock.get("/simple/price").mock(return_value=httpx.Response(500))
        adapter = CoinGeckoAdapter()
        with pytest.raises(DataGap):
            adapter.get_price("BTC")
```

- [ ] **Step 3: Run, expect ImportError**

Run:

```bash
pytest tests/test_data_coingecko.py -v
```

Expected: `ImportError`.

- [ ] **Step 4: Implement CoinGecko adapter**

Create `engine/crypto_claw_engine/data/coingecko.py`:

```python
import httpx

from crypto_claw_engine.data.base import PriceSnapshot
from crypto_claw_engine.errors import DataGap

SYMBOL_TO_ID = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "ADA": "cardano",
    "AVAX": "avalanche-2",
    "DOGE": "dogecoin",
    "LINK": "chainlink",
    "DOT": "polkadot",
}


class CoinGeckoAdapter:
    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self, client: httpx.Client | None = None, timeout: float = 10.0):
        self._client = client or httpx.Client(base_url=self.BASE_URL, timeout=timeout)

    def get_price(self, symbol: str) -> PriceSnapshot:
        coin_id = SYMBOL_TO_ID.get(symbol.upper())
        if not coin_id:
            raise DataGap("coingecko", symbol, "unknown symbol")
        try:
            r = self._client.get(
                "/simple/price",
                params={
                    "ids": coin_id,
                    "vs_currencies": "usd",
                    "include_market_cap": "true",
                    "include_24hr_vol": "true",
                },
            )
            r.raise_for_status()
        except httpx.HTTPError as e:
            raise DataGap("coingecko", symbol, f"http error: {e}") from e

        data = r.json().get(coin_id)
        if not data or "usd" not in data:
            raise DataGap("coingecko", symbol, "no price in response")

        return PriceSnapshot(
            symbol=symbol.upper(),
            price_usd=float(data["usd"]),
            market_cap_usd=data.get("usd_market_cap"),
            volume_24h_usd=data.get("usd_24h_vol"),
        )
```

- [ ] **Step 5: Run tests, expect pass**

Run:

```bash
pytest tests/test_data_coingecko.py -v
```

Expected: `3 passed`.

- [ ] **Step 6: Commit**

```bash
git add engine/tests/fixtures/coingecko_*.json engine/crypto_claw_engine/data/coingecko.py engine/tests/test_data_coingecko.py
git commit -m "feat(engine): CoinGecko price adapter with DataGap on failure"
```

---

## Task 6: Binance Adapter

**Files:**
- Create: `engine/tests/fixtures/binance_klines_btc.json`
- Create: `engine/tests/fixtures/binance_funding_btc.json`
- Create: `engine/tests/fixtures/binance_oi_btc.json`
- Create: `engine/crypto_claw_engine/data/binance.py`
- Create: `engine/tests/test_data_binance.py`

- [ ] **Step 1: Create fixtures**

Create `engine/tests/fixtures/binance_klines_btc.json`:

```json
[
  [1712534400000, "64000.00", "65500.00", "63800.00", "65000.00", "1234.56", 1712620799999, "80000000.00", 9999, "617.28", "40000000.00", "0"],
  [1712620800000, "65000.00", "66200.00", "64700.00", "65800.00", "1456.78", 1712707199999, "95000000.00", 10234, "728.39", "47500000.00", "0"],
  [1712707200000, "65800.00", "67000.00", "65500.00", "66500.00", "1523.45", 1712793599999, "101000000.00", 10567, "761.73", "50500000.00", "0"]
]
```

Create `engine/tests/fixtures/binance_funding_btc.json`:

```json
[
  {"symbol": "BTCUSDT", "fundingTime": 1712534400000, "fundingRate": "0.00010000"},
  {"symbol": "BTCUSDT", "fundingTime": 1712563200000, "fundingRate": "0.00012500"},
  {"symbol": "BTCUSDT", "fundingTime": 1712592000000, "fundingRate": "0.00008000"}
]
```

Create `engine/tests/fixtures/binance_oi_btc.json`:

```json
{"symbol": "BTCUSDT", "openInterest": "82000.500", "time": 1712707200000}
```

- [ ] **Step 2: Write failing test**

Create `engine/tests/test_data_binance.py`:

```python
import httpx
import pytest
import respx

from crypto_claw_engine.data.binance import BinanceAdapter
from crypto_claw_engine.errors import DataGap


def test_get_ohlcv_parses_klines(load_fixture):
    with respx.mock() as mock:
        mock.get("https://api.binance.com/api/v3/klines").mock(
            return_value=httpx.Response(200, json=load_fixture("binance_klines_btc.json"))
        )
        adapter = BinanceAdapter()
        bars = adapter.get_ohlcv("BTC", interval="1d", limit=3)
        assert len(bars) == 3
        assert bars[0].open == 64000.0
        assert bars[0].close == 65000.0
        assert bars[-1].close == 66500.0


def test_get_funding_parses(load_fixture):
    with respx.mock() as mock:
        mock.get("https://fapi.binance.com/fapi/v1/fundingRate").mock(
            return_value=httpx.Response(200, json=load_fixture("binance_funding_btc.json"))
        )
        adapter = BinanceAdapter()
        snaps = adapter.get_funding("BTC", limit=3)
        assert len(snaps) == 3
        assert snaps[0].funding_rate == 0.0001
        assert snaps[0].symbol == "BTCUSDT"


def test_get_open_interest_parses(load_fixture):
    with respx.mock() as mock:
        mock.get("https://fapi.binance.com/fapi/v1/openInterest").mock(
            return_value=httpx.Response(200, json=load_fixture("binance_oi_btc.json"))
        )
        # Also need a klines call to convert contracts -> USD via last close, or skip USD conversion.
        adapter = BinanceAdapter()
        snap = adapter.get_open_interest("BTC")
        assert snap.funding_rate == 0.0  # not applicable; default
        assert snap.open_interest_usd is None or snap.open_interest_usd > 0


def test_ohlcv_http_error_raises_data_gap():
    with respx.mock() as mock:
        mock.get("https://api.binance.com/api/v3/klines").mock(return_value=httpx.Response(503))
        adapter = BinanceAdapter()
        with pytest.raises(DataGap):
            adapter.get_ohlcv("BTC", interval="1d", limit=3)
```

- [ ] **Step 3: Run, expect ImportError**

Run:

```bash
pytest tests/test_data_binance.py -v
```

Expected: `ImportError`.

- [ ] **Step 4: Implement Binance adapter**

Create `engine/crypto_claw_engine/data/binance.py`:

```python
from datetime import datetime, timezone

import httpx

from crypto_claw_engine.data.base import DerivSnapshot, OHLCVBar
from crypto_claw_engine.errors import DataGap

SPOT_URL = "https://api.binance.com"
FUT_URL = "https://fapi.binance.com"


def _to_symbol(asset: str) -> str:
    return f"{asset.upper()}USDT"


class BinanceAdapter:
    def __init__(self, client: httpx.Client | None = None, timeout: float = 10.0):
        self._client = client or httpx.Client(timeout=timeout)

    def get_ohlcv(self, asset: str, interval: str = "1d", limit: int = 100) -> list[OHLCVBar]:
        symbol = _to_symbol(asset)
        try:
            r = self._client.get(
                f"{SPOT_URL}/api/v3/klines",
                params={"symbol": symbol, "interval": interval, "limit": limit},
            )
            r.raise_for_status()
        except httpx.HTTPError as e:
            raise DataGap("binance", symbol, f"klines http error: {e}") from e

        rows = r.json()
        if not rows:
            raise DataGap("binance", symbol, "empty klines response")

        return [
            OHLCVBar(
                open_time=datetime.fromtimestamp(row[0] / 1000, tz=timezone.utc),
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=float(row[5]),
            )
            for row in rows
        ]

    def get_funding(self, asset: str, limit: int = 30) -> list[DerivSnapshot]:
        symbol = _to_symbol(asset)
        try:
            r = self._client.get(
                f"{FUT_URL}/fapi/v1/fundingRate",
                params={"symbol": symbol, "limit": limit},
            )
            r.raise_for_status()
        except httpx.HTTPError as e:
            raise DataGap("binance", symbol, f"funding http error: {e}") from e

        rows = r.json()
        if not rows:
            raise DataGap("binance", symbol, "empty funding response")

        return [
            DerivSnapshot(
                symbol=row["symbol"],
                funding_rate=float(row["fundingRate"]),
                as_of=datetime.fromtimestamp(row["fundingTime"] / 1000, tz=timezone.utc),
            )
            for row in rows
        ]

    def get_open_interest(self, asset: str) -> DerivSnapshot:
        symbol = _to_symbol(asset)
        try:
            r = self._client.get(
                f"{FUT_URL}/fapi/v1/openInterest",
                params={"symbol": symbol},
            )
            r.raise_for_status()
        except httpx.HTTPError as e:
            raise DataGap("binance", symbol, f"OI http error: {e}") from e

        data = r.json()
        return DerivSnapshot(
            symbol=data["symbol"],
            funding_rate=0.0,  # OI endpoint does not return funding
            open_interest_usd=None,  # raw is in contracts; USD conversion deferred
            as_of=datetime.fromtimestamp(data["time"] / 1000, tz=timezone.utc),
        )
```

- [ ] **Step 5: Run tests, expect pass**

Run:

```bash
pytest tests/test_data_binance.py -v
```

Expected: `4 passed`.

- [ ] **Step 6: Commit**

```bash
git add engine/tests/fixtures/binance_*.json engine/crypto_claw_engine/data/binance.py engine/tests/test_data_binance.py
git commit -m "feat(engine): Binance public REST adapter (klines, funding, OI)"
```

---

## Task 7: AgentBase

**Files:**
- Create: `engine/crypto_claw_engine/agents/__init__.py`
- Create: `engine/crypto_claw_engine/agents/base.py`
- Create: `engine/tests/test_agent_base.py`

- [ ] **Step 1: Write failing test**

Create `engine/tests/test_agent_base.py`:

```python
from crypto_claw_engine.agents.base import AgentBase, AgentContext
from crypto_claw_engine.llm import FakeLLM
from crypto_claw_engine.models import AgentSignal, Portfolio, RunRequest


class DummyAgent(AgentBase):
    name = "dummy"

    def analyze(self, asset: str, ctx: AgentContext) -> AgentSignal:
        return AgentSignal(
            agent=self.name,
            asset=asset,
            stance="neutral",
            confidence=0.5,
            rationale="dummy",
            evidence={"x": 1},
        )


def test_agent_base_run_for_all_assets():
    req = RunRequest(universe=["BTC", "ETH"], portfolio=Portfolio(cash_usd=1000))
    ctx = AgentContext(request=req, data={}, llm=FakeLLM())
    agent = DummyAgent()
    signals = agent.run(ctx)
    assert len(signals) == 2
    assert {s.asset for s in signals} == {"BTC", "ETH"}
    assert all(s.agent == "dummy" for s in signals)
```

- [ ] **Step 2: Run, expect ImportError**

Run:

```bash
pytest tests/test_agent_base.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement base.py**

Create `engine/crypto_claw_engine/agents/__init__.py` as an empty file.

Create `engine/crypto_claw_engine/agents/base.py`:

```python
from dataclasses import dataclass, field
from typing import Any

from crypto_claw_engine.llm import LLMClient
from crypto_claw_engine.models import AgentSignal, RunRequest


@dataclass
class AgentContext:
    request: RunRequest
    data: dict[str, Any] = field(default_factory=dict)  # arbitrary pre-fetched data by key
    llm: LLMClient | None = None


class AgentBase:
    name: str = "base"

    def analyze(self, asset: str, ctx: AgentContext) -> AgentSignal:
        raise NotImplementedError

    def run(self, ctx: AgentContext) -> list[AgentSignal]:
        out: list[AgentSignal] = []
        for asset in ctx.request.universe:
            out.append(self.analyze(asset, ctx))
        return out
```

- [ ] **Step 4: Run tests, expect pass**

Run:

```bash
pytest tests/test_agent_base.py -v
```

Expected: `1 passed`.

- [ ] **Step 5: Commit**

```bash
git add engine/crypto_claw_engine/agents/ engine/tests/test_agent_base.py
git commit -m "feat(engine): AgentBase and AgentContext"
```

---

## Task 8: TechnicalsAgent

**Files:**
- Create: `engine/crypto_claw_engine/agents/technicals.py`
- Create: `engine/tests/test_agent_technicals.py`

**Feature computation rules:**
- RSI(14) on closes
- Trend: (close[-1] - close[-20]) / close[-20]
- Volatility: ATR(14) / close[-1]
- Stance: `bullish` if RSI<35 and trend>0 or trend>0.05; `bearish` if RSI>70 and trend<0 or trend<-0.05; else `neutral`
- Confidence: 0.5 baseline, +0.2 if RSI extreme confirms, +0.15 if trend strong
- Rationale: LLM (FakeLLM for now)

- [ ] **Step 1: Write failing test**

Create `engine/tests/test_agent_technicals.py`:

```python
from datetime import datetime, timedelta, timezone

from crypto_claw_engine.agents.base import AgentContext
from crypto_claw_engine.agents.technicals import TechnicalsAgent
from crypto_claw_engine.data.base import OHLCVBar
from crypto_claw_engine.llm import FakeLLM
from crypto_claw_engine.models import Portfolio, RunRequest


def _synth_bars(closes: list[float]) -> list[OHLCVBar]:
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    out = []
    for i, c in enumerate(closes):
        out.append(
            OHLCVBar(
                open_time=base + timedelta(days=i),
                open=c,
                high=c * 1.01,
                low=c * 0.99,
                close=c,
                volume=1000.0,
            )
        )
    return out


def _ctx(bars_by_asset: dict):
    req = RunRequest(universe=list(bars_by_asset.keys()), portfolio=Portfolio(cash_usd=1000))
    return AgentContext(
        request=req,
        data={"ohlcv": bars_by_asset},
        llm=FakeLLM({"technicals": "technicals narrative"}),
    )


def test_technicals_bullish_on_strong_uptrend():
    closes = [100 + i * 2 for i in range(30)]  # monotonically rising
    ctx = _ctx({"BTC": _synth_bars(closes)})
    agent = TechnicalsAgent()
    sigs = agent.run(ctx)
    assert len(sigs) == 1
    assert sigs[0].stance == "bullish"
    assert sigs[0].rationale == "technicals narrative"
    assert "rsi" in sigs[0].evidence


def test_technicals_bearish_on_strong_downtrend():
    closes = [200 - i * 3 for i in range(30)]
    ctx = _ctx({"BTC": _synth_bars(closes)})
    agent = TechnicalsAgent()
    sigs = agent.run(ctx)
    assert sigs[0].stance == "bearish"


def test_technicals_neutral_on_flat():
    closes = [100 + ((-1) ** i) * 0.5 for i in range(30)]
    ctx = _ctx({"BTC": _synth_bars(closes)})
    agent = TechnicalsAgent()
    sigs = agent.run(ctx)
    assert sigs[0].stance == "neutral"


def test_technicals_missing_data_returns_neutral_zero_confidence():
    ctx = _ctx({"BTC": []})
    agent = TechnicalsAgent()
    sigs = agent.run(ctx)
    assert sigs[0].stance == "neutral"
    assert sigs[0].confidence == 0.0
    assert "unavailable" in sigs[0].rationale.lower()
```

- [ ] **Step 2: Run, expect ImportError**

Run:

```bash
pytest tests/test_agent_technicals.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement TechnicalsAgent**

Create `engine/crypto_claw_engine/agents/technicals.py`:

```python
import pandas as pd
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

from crypto_claw_engine.agents.base import AgentBase, AgentContext
from crypto_claw_engine.models import AgentSignal


class TechnicalsAgent(AgentBase):
    name = "technicals"

    def analyze(self, asset: str, ctx: AgentContext) -> AgentSignal:
        bars = (ctx.data.get("ohlcv") or {}).get(asset) or []
        if len(bars) < 20:
            return AgentSignal(
                agent=self.name,
                asset=asset,
                stance="neutral",
                confidence=0.0,
                rationale="Data unavailable (not enough OHLCV bars).",
                evidence={"bars": len(bars)},
            )

        df = pd.DataFrame(
            {
                "open": [b.open for b in bars],
                "high": [b.high for b in bars],
                "low": [b.low for b in bars],
                "close": [b.close for b in bars],
                "volume": [b.volume for b in bars],
            }
        )

        rsi = RSIIndicator(df["close"], window=14).rsi().iloc[-1]
        atr = AverageTrueRange(df["high"], df["low"], df["close"], window=14).average_true_range().iloc[-1]
        last = df["close"].iloc[-1]
        past = df["close"].iloc[-20]
        trend = (last - past) / past if past else 0.0
        volatility = (atr / last) if last else 0.0

        stance = "neutral"
        confidence = 0.5
        if (rsi < 35 and trend > 0) or trend > 0.05:
            stance = "bullish"
            if rsi < 35:
                confidence += 0.2
            if trend > 0.05:
                confidence += 0.15
        elif (rsi > 70 and trend < 0) or trend < -0.05:
            stance = "bearish"
            if rsi > 70:
                confidence += 0.2
            if trend < -0.05:
                confidence += 0.15

        confidence = min(confidence, 1.0)

        evidence = {
            "rsi": round(float(rsi), 2),
            "trend_20d_pct": round(float(trend) * 100, 2),
            "atr_pct": round(float(volatility) * 100, 2),
            "last_close": round(float(last), 2),
        }

        rationale = (
            ctx.llm.complete(
                messages=[
                    {
                        "role": "user",
                        "content": f"Assess {asset} from evidence: {evidence}. Stance: {stance}.",
                    }
                ],
                tag="technicals",
            )
            if ctx.llm
            else f"{asset} technicals {stance}; evidence: {evidence}"
        )

        return AgentSignal(
            agent=self.name,
            asset=asset,
            stance=stance,
            confidence=confidence,
            rationale=rationale,
            evidence=evidence,
        )
```

- [ ] **Step 4: Run tests, expect pass**

Run:

```bash
pytest tests/test_agent_technicals.py -v
```

Expected: `4 passed`.

- [ ] **Step 5: Commit**

```bash
git add engine/crypto_claw_engine/agents/technicals.py engine/tests/test_agent_technicals.py
git commit -m "feat(engine): TechnicalsAgent with RSI/ATR/trend features"
```

---

## Task 9: DerivativesAgent

**Files:**
- Create: `engine/crypto_claw_engine/agents/derivatives.py`
- Create: `engine/tests/test_agent_derivatives.py`

**Feature rules:**
- Avg funding rate over last N snapshots
- Stance: `bearish` if avg_funding > 0.0003 (crowded longs); `bullish` if avg_funding < -0.0001; else `neutral`
- Confidence: scaled by magnitude
- Evidence: {avg_funding, num_snapshots}

- [ ] **Step 1: Write failing test**

Create `engine/tests/test_agent_derivatives.py`:

```python
from datetime import datetime, timezone

from crypto_claw_engine.agents.base import AgentContext
from crypto_claw_engine.agents.derivatives import DerivativesAgent
from crypto_claw_engine.data.base import DerivSnapshot
from crypto_claw_engine.llm import FakeLLM
from crypto_claw_engine.models import Portfolio, RunRequest


def _snaps(rates: list[float]) -> list[DerivSnapshot]:
    return [
        DerivSnapshot(
            symbol="BTCUSDT",
            funding_rate=r,
            as_of=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        for r in rates
    ]


def _ctx(funding: dict):
    req = RunRequest(universe=list(funding.keys()), portfolio=Portfolio(cash_usd=1000))
    return AgentContext(
        request=req,
        data={"funding": funding},
        llm=FakeLLM({"derivatives": "deriv narrative"}),
    )


def test_bearish_on_crowded_longs():
    ctx = _ctx({"BTC": _snaps([0.0005, 0.0006, 0.0004])})
    sigs = DerivativesAgent().run(ctx)
    assert sigs[0].stance == "bearish"
    assert sigs[0].rationale == "deriv narrative"
    assert "avg_funding" in sigs[0].evidence


def test_bullish_on_negative_funding():
    ctx = _ctx({"BTC": _snaps([-0.0002, -0.0003, -0.0001])})
    sigs = DerivativesAgent().run(ctx)
    assert sigs[0].stance == "bullish"


def test_neutral_on_mild_funding():
    ctx = _ctx({"BTC": _snaps([0.00005, 0.00002, 0.00001])})
    sigs = DerivativesAgent().run(ctx)
    assert sigs[0].stance == "neutral"


def test_missing_funding_data_degrades_to_neutral():
    ctx = _ctx({"BTC": []})
    sigs = DerivativesAgent().run(ctx)
    assert sigs[0].stance == "neutral"
    assert sigs[0].confidence == 0.0
```

- [ ] **Step 2: Run, expect ImportError**

Run:

```bash
pytest tests/test_agent_derivatives.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement DerivativesAgent**

Create `engine/crypto_claw_engine/agents/derivatives.py`:

```python
from crypto_claw_engine.agents.base import AgentBase, AgentContext
from crypto_claw_engine.models import AgentSignal


class DerivativesAgent(AgentBase):
    name = "derivatives"

    def analyze(self, asset: str, ctx: AgentContext) -> AgentSignal:
        snaps = (ctx.data.get("funding") or {}).get(asset) or []
        if not snaps:
            return AgentSignal(
                agent=self.name,
                asset=asset,
                stance="neutral",
                confidence=0.0,
                rationale="Data unavailable (no funding snapshots).",
                evidence={"snapshots": 0},
            )

        rates = [s.funding_rate for s in snaps]
        avg = sum(rates) / len(rates)

        stance = "neutral"
        confidence = 0.5
        if avg > 0.0003:
            stance = "bearish"
            confidence = min(0.5 + avg * 500, 0.95)
        elif avg < -0.0001:
            stance = "bullish"
            confidence = min(0.5 + abs(avg) * 500, 0.95)

        evidence = {
            "avg_funding": round(float(avg), 6),
            "snapshots": len(rates),
            "latest_funding": round(float(rates[-1]), 6),
        }

        rationale = (
            ctx.llm.complete(
                messages=[
                    {
                        "role": "user",
                        "content": f"Assess {asset} derivatives: {evidence}. Stance: {stance}.",
                    }
                ],
                tag="derivatives",
            )
            if ctx.llm
            else f"{asset} derivatives {stance}; evidence: {evidence}"
        )

        return AgentSignal(
            agent=self.name,
            asset=asset,
            stance=stance,
            confidence=confidence,
            rationale=rationale,
            evidence=evidence,
        )
```

- [ ] **Step 4: Run tests, expect pass**

Run:

```bash
pytest tests/test_agent_derivatives.py -v
```

Expected: `4 passed`.

- [ ] **Step 5: Commit**

```bash
git add engine/crypto_claw_engine/agents/derivatives.py engine/tests/test_agent_derivatives.py
git commit -m "feat(engine): DerivativesAgent based on funding rate"
```

---

## Task 10: TailRiskAgent

**Files:**
- Create: `engine/crypto_claw_engine/agents/tail_risk.py`
- Create: `engine/tests/test_agent_tail_risk.py`

**Feature rules:**
- Compute 30-day realized volatility (stdev of log returns)
- Compute max drawdown in the window
- Compute 60-day baseline vol; regime_shift = (vol_30d / vol_60d) - 1
- Stance: `bearish` if regime_shift > 0.3 (vol spiking up) or drawdown < -0.2; else `neutral`
- Rarely bullish: only if vol compressed below 0.7× baseline and drawdown recovering
- Evidence: vol_30d, vol_60d, regime_shift, max_drawdown

- [ ] **Step 1: Write failing test**

Create `engine/tests/test_agent_tail_risk.py`:

```python
from datetime import datetime, timedelta, timezone
import math

from crypto_claw_engine.agents.base import AgentContext
from crypto_claw_engine.agents.tail_risk import TailRiskAgent
from crypto_claw_engine.data.base import OHLCVBar
from crypto_claw_engine.llm import FakeLLM
from crypto_claw_engine.models import Portfolio, RunRequest


def _bars(closes: list[float]) -> list[OHLCVBar]:
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return [
        OHLCVBar(
            open_time=base + timedelta(days=i),
            open=c,
            high=c * 1.02,
            low=c * 0.98,
            close=c,
            volume=1.0,
        )
        for i, c in enumerate(closes)
    ]


def _ctx(bars_by_asset: dict):
    req = RunRequest(universe=list(bars_by_asset.keys()), portfolio=Portfolio(cash_usd=1000))
    return AgentContext(
        request=req,
        data={"ohlcv": bars_by_asset},
        llm=FakeLLM({"tail_risk": "tail narrative"}),
    )


def test_tail_risk_bearish_on_deep_drawdown():
    closes = [100] * 40 + [80 - i for i in range(30)]  # sudden sharp drawdown
    ctx = _ctx({"BTC": _bars(closes)})
    sigs = TailRiskAgent().run(ctx)
    assert sigs[0].stance == "bearish"
    assert "max_drawdown" in sigs[0].evidence


def test_tail_risk_neutral_on_calm_market():
    closes = [100 + math.sin(i / 5) * 0.5 for i in range(80)]
    ctx = _ctx({"BTC": _bars(closes)})
    sigs = TailRiskAgent().run(ctx)
    assert sigs[0].stance == "neutral"


def test_tail_risk_missing_data_returns_zero_conf():
    ctx = _ctx({"BTC": _bars([100] * 5)})
    sigs = TailRiskAgent().run(ctx)
    assert sigs[0].stance == "neutral"
    assert sigs[0].confidence == 0.0
```

- [ ] **Step 2: Run, expect ImportError**

Run:

```bash
pytest tests/test_agent_tail_risk.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement TailRiskAgent**

Create `engine/crypto_claw_engine/agents/tail_risk.py`:

```python
import math

from crypto_claw_engine.agents.base import AgentBase, AgentContext
from crypto_claw_engine.models import AgentSignal


def _log_returns(closes: list[float]) -> list[float]:
    out = []
    for i in range(1, len(closes)):
        if closes[i - 1] <= 0:
            continue
        out.append(math.log(closes[i] / closes[i - 1]))
    return out


def _stdev(xs: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    mean = sum(xs) / len(xs)
    var = sum((x - mean) ** 2 for x in xs) / (len(xs) - 1)
    return math.sqrt(var)


class TailRiskAgent(AgentBase):
    name = "tail_risk"

    def analyze(self, asset: str, ctx: AgentContext) -> AgentSignal:
        bars = (ctx.data.get("ohlcv") or {}).get(asset) or []
        if len(bars) < 60:
            return AgentSignal(
                agent=self.name,
                asset=asset,
                stance="neutral",
                confidence=0.0,
                rationale="Data unavailable (need >=60 bars for regime analysis).",
                evidence={"bars": len(bars)},
            )

        closes = [b.close for b in bars]
        rets = _log_returns(closes)
        vol_30 = _stdev(rets[-30:])
        vol_60 = _stdev(rets[-60:])
        regime_shift = (vol_30 / vol_60 - 1.0) if vol_60 > 0 else 0.0

        window = closes[-60:]
        peak = max(window)
        trough_after_peak = min(window[window.index(peak):]) if peak in window else min(window)
        max_dd = (trough_after_peak - peak) / peak if peak else 0.0

        stance = "neutral"
        confidence = 0.5
        if regime_shift > 0.3 or max_dd < -0.2:
            stance = "bearish"
            confidence = min(0.6 + max(regime_shift, abs(max_dd)), 0.95)
        elif regime_shift < -0.3 and max_dd > -0.05:
            stance = "bullish"
            confidence = 0.6

        evidence = {
            "vol_30d": round(vol_30, 5),
            "vol_60d": round(vol_60, 5),
            "regime_shift": round(regime_shift, 3),
            "max_drawdown": round(max_dd, 3),
        }

        rationale = (
            ctx.llm.complete(
                messages=[
                    {
                        "role": "user",
                        "content": f"Tail risk for {asset}: {evidence}. Stance: {stance}.",
                    }
                ],
                tag="tail_risk",
            )
            if ctx.llm
            else f"{asset} tail risk {stance}; evidence: {evidence}"
        )

        return AgentSignal(
            agent=self.name,
            asset=asset,
            stance=stance,
            confidence=confidence,
            rationale=rationale,
            evidence=evidence,
        )
```

- [ ] **Step 4: Run tests, expect pass**

Run:

```bash
pytest tests/test_agent_tail_risk.py -v
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
git add engine/crypto_claw_engine/agents/tail_risk.py engine/tests/test_agent_tail_risk.py
git commit -m "feat(engine): TailRiskAgent with vol regime and drawdown"
```

---

## Task 11: PortfolioManagerAgent

**Files:**
- Create: `engine/crypto_claw_engine/agents/portfolio_manager.py`
- Create: `engine/tests/test_agent_portfolio_manager.py`

**Decision logic:**
- For each asset, aggregate contributing signals (same asset, from other agents)
- Compute consensus = sum(stance_vote * confidence) / sum(confidence), where bullish=+1, bearish=-1, neutral=0
- If consensus > 0.3 and total_confidence > 0.8 → action="buy", size_pct = round(0.1 * consensus, 2)
- If consensus < -0.3 and total_confidence > 0.8 → action="sell", size_pct = round(0.1 * abs(consensus), 2)
- Else action="hold", size_pct=0.0
- Final confidence = min(1.0, total_confidence / num_signals)
- Reasoning: LLM (FakeLLM)
- Risk notes: empty for M1 (RiskManager deferred)

PortfolioManagerAgent is special: it does not use `analyze(asset, ctx)` directly. It consumes upstream signals from ctx.data["upstream_signals"].

- [ ] **Step 1: Write failing test**

Create `engine/tests/test_agent_portfolio_manager.py`:

```python
from crypto_claw_engine.agents.base import AgentContext
from crypto_claw_engine.agents.portfolio_manager import PortfolioManagerAgent
from crypto_claw_engine.llm import FakeLLM
from crypto_claw_engine.models import AgentSignal, Portfolio, RunRequest


def _sig(agent: str, asset: str, stance: str, conf: float) -> AgentSignal:
    return AgentSignal(
        agent=agent,
        asset=asset,
        stance=stance,
        confidence=conf,
        rationale="...",
        evidence={},
    )


def _ctx(signals):
    req = RunRequest(universe=list({s.asset for s in signals}), portfolio=Portfolio(cash_usd=1000))
    return AgentContext(
        request=req,
        data={"upstream_signals": signals},
        llm=FakeLLM({"portfolio_manager": "pm narrative"}),
    )


def test_pm_buys_on_strong_consensus():
    sigs = [
        _sig("technicals", "BTC", "bullish", 0.8),
        _sig("derivatives", "BTC", "bullish", 0.7),
        _sig("tail_risk", "BTC", "neutral", 0.5),
    ]
    decisions = PortfolioManagerAgent().make_decisions(_ctx(sigs))
    assert len(decisions) == 1
    assert decisions[0].action == "buy"
    assert decisions[0].size_pct > 0
    assert decisions[0].reasoning == "pm narrative"
    assert len(decisions[0].contributing_signals) == 3


def test_pm_sells_on_strong_bearish_consensus():
    sigs = [
        _sig("technicals", "ETH", "bearish", 0.8),
        _sig("derivatives", "ETH", "bearish", 0.9),
        _sig("tail_risk", "ETH", "bearish", 0.75),
    ]
    decisions = PortfolioManagerAgent().make_decisions(_ctx(sigs))
    assert decisions[0].action == "sell"
    assert decisions[0].size_pct > 0


def test_pm_holds_on_mixed_signals():
    sigs = [
        _sig("technicals", "SOL", "bullish", 0.6),
        _sig("derivatives", "SOL", "bearish", 0.6),
        _sig("tail_risk", "SOL", "neutral", 0.4),
    ]
    decisions = PortfolioManagerAgent().make_decisions(_ctx(sigs))
    assert decisions[0].action == "hold"
    assert decisions[0].size_pct == 0.0


def test_pm_handles_multi_asset():
    sigs = [
        _sig("technicals", "BTC", "bullish", 0.9),
        _sig("derivatives", "BTC", "bullish", 0.8),
        _sig("tail_risk", "BTC", "neutral", 0.5),
        _sig("technicals", "ETH", "bearish", 0.85),
        _sig("derivatives", "ETH", "bearish", 0.7),
        _sig("tail_risk", "ETH", "bearish", 0.6),
    ]
    decisions = PortfolioManagerAgent().make_decisions(_ctx(sigs))
    by_asset = {d.asset: d for d in decisions}
    assert by_asset["BTC"].action == "buy"
    assert by_asset["ETH"].action == "sell"
```

- [ ] **Step 2: Run, expect ImportError**

Run:

```bash
pytest tests/test_agent_portfolio_manager.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement PortfolioManagerAgent**

Create `engine/crypto_claw_engine/agents/portfolio_manager.py`:

```python
from collections import defaultdict

from crypto_claw_engine.agents.base import AgentContext
from crypto_claw_engine.models import AgentSignal, Decision

STANCE_VOTE = {"bullish": 1, "bearish": -1, "neutral": 0}


class PortfolioManagerAgent:
    name = "portfolio_manager"

    def make_decisions(self, ctx: AgentContext) -> list[Decision]:
        signals: list[AgentSignal] = ctx.data.get("upstream_signals", [])
        by_asset: dict[str, list[AgentSignal]] = defaultdict(list)
        for s in signals:
            by_asset[s.asset].append(s)

        decisions: list[Decision] = []
        for asset, sigs in by_asset.items():
            total_conf = sum(s.confidence for s in sigs) or 1e-9
            consensus = sum(STANCE_VOTE[s.stance] * s.confidence for s in sigs) / total_conf
            avg_conf = total_conf / len(sigs)

            if consensus > 0.3 and total_conf > 0.8:
                action = "buy"
                size_pct = round(0.1 * consensus, 2)
            elif consensus < -0.3 and total_conf > 0.8:
                action = "sell"
                size_pct = round(0.1 * abs(consensus), 2)
            else:
                action = "hold"
                size_pct = 0.0

            rationale = (
                ctx.llm.complete(
                    messages=[
                        {
                            "role": "user",
                            "content": (
                                f"Synthesize a crypto position decision for {asset}. "
                                f"Consensus: {round(consensus, 2)}. Avg confidence: {round(avg_conf, 2)}. "
                                f"Action: {action}."
                            ),
                        }
                    ],
                    tag="portfolio_manager",
                )
                if ctx.llm
                else f"{asset} {action}; consensus {round(consensus, 2)}."
            )

            decisions.append(
                Decision(
                    asset=asset,
                    action=action,
                    size_pct=size_pct,
                    confidence=min(avg_conf, 1.0),
                    reasoning=rationale,
                    contributing_signals=sigs,
                    risk_notes="",
                )
            )

        return decisions
```

- [ ] **Step 4: Run tests, expect pass**

Run:

```bash
pytest tests/test_agent_portfolio_manager.py -v
```

Expected: `4 passed`.

- [ ] **Step 5: Commit**

```bash
git add engine/crypto_claw_engine/agents/portfolio_manager.py engine/tests/test_agent_portfolio_manager.py
git commit -m "feat(engine): PortfolioManagerAgent with consensus-based decisions"
```

---

## Task 12: LangGraph Runner

**Files:**
- Create: `engine/crypto_claw_engine/graph/__init__.py`
- Create: `engine/crypto_claw_engine/graph/runner.py`
- Create: `engine/tests/test_graph_runner.py`

**Runner responsibilities:**
- Accept a RunRequest + PriceSource + DerivSource + LLMClient
- Fetch OHLCV for each asset (Binance klines, interval=1d, limit=80)
- Fetch funding for each asset (Binance, limit=30)
- Run TechnicalsAgent, DerivativesAgent, TailRiskAgent sequentially (Tier A — LangGraph parallel is scaffolded but a plain loop is acceptable for M1; the graph module exists for M2 parallelism)
- Pipe signals into PortfolioManagerAgent
- Return RunResult
- Any agent that raises is caught; asset gets a failure signal and `agents_failed` grows

For M1, `runner.run()` uses a sequential for-loop rather than LangGraph's StateGraph to keep the surface simple. The module is named `graph/` and the parallel DAG will land in M2.

- [ ] **Step 1: Write failing test**

Create `engine/tests/test_graph_runner.py`:

```python
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from crypto_claw_engine.data.base import DerivSnapshot, OHLCVBar
from crypto_claw_engine.graph.runner import run_engine
from crypto_claw_engine.llm import FakeLLM
from crypto_claw_engine.models import Portfolio, RunRequest


def _bars(closes: list[float]) -> list[OHLCVBar]:
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return [
        OHLCVBar(
            open_time=base + timedelta(days=i),
            open=c,
            high=c * 1.01,
            low=c * 0.99,
            close=c,
            volume=10.0,
        )
        for i, c in enumerate(closes)
    ]


def _funding(rates: list[float]) -> list[DerivSnapshot]:
    return [
        DerivSnapshot(
            symbol="BTCUSDT",
            funding_rate=r,
            as_of=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        for r in rates
    ]


def test_run_engine_end_to_end_produces_decisions():
    price = MagicMock()
    price.get_ohlcv.return_value = _bars([100 + i * 2 for i in range(80)])

    deriv = MagicMock()
    deriv.get_funding.return_value = _funding([0.0005] * 10)

    req = RunRequest(universe=["BTC"], portfolio=Portfolio(cash_usd=1000))
    result = run_engine(
        request=req,
        price_source=price,
        deriv_source=deriv,
        llm=FakeLLM({"portfolio_manager": "pm"}),
    )

    assert result.run_id
    assert len(result.decisions) == 1
    assert len(result.signals) == 3  # technicals + derivatives + tail_risk
    assert not result.agents_failed


def test_run_engine_degrades_on_data_gap():
    price = MagicMock()
    price.get_ohlcv.side_effect = Exception("boom")

    deriv = MagicMock()
    deriv.get_funding.return_value = _funding([0.0001] * 10)

    req = RunRequest(universe=["BTC"], portfolio=Portfolio(cash_usd=1000))
    result = run_engine(
        request=req,
        price_source=price,
        deriv_source=deriv,
        llm=FakeLLM(),
    )

    # Technicals + TailRisk should both produce neutral zero-confidence signals.
    neutral_zero = [
        s for s in result.signals if s.stance == "neutral" and s.confidence == 0.0
    ]
    assert len(neutral_zero) >= 2  # technicals and tail_risk
    # Derivatives should still work.
    assert any(s.agent == "derivatives" and s.confidence > 0 for s in result.signals)
```

- [ ] **Step 2: Run, expect ImportError**

Run:

```bash
pytest tests/test_graph_runner.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement runner.py**

Create `engine/crypto_claw_engine/graph/__init__.py` as an empty file.

Create `engine/crypto_claw_engine/graph/runner.py`:

```python
import uuid
from datetime import datetime, timezone

from crypto_claw_engine.agents.base import AgentContext
from crypto_claw_engine.agents.derivatives import DerivativesAgent
from crypto_claw_engine.agents.portfolio_manager import PortfolioManagerAgent
from crypto_claw_engine.agents.tail_risk import TailRiskAgent
from crypto_claw_engine.agents.technicals import TechnicalsAgent
from crypto_claw_engine.data.base import DerivSource, PriceSource
from crypto_claw_engine.llm import LLMClient
from crypto_claw_engine.models import RunRequest, RunResult

TIER_A_AGENTS = [TechnicalsAgent(), DerivativesAgent(), TailRiskAgent()]


def _fetch_ohlcv(price_source: PriceSource, universe: list[str]) -> dict[str, list]:
    out = {}
    for asset in universe:
        try:
            out[asset] = price_source.get_ohlcv(asset, "1d", 80)
        except Exception:
            out[asset] = []
    return out


def _fetch_funding(deriv_source: DerivSource, universe: list[str]) -> dict[str, list]:
    out = {}
    for asset in universe:
        try:
            out[asset] = deriv_source.get_funding(asset, 30)
        except Exception:
            out[asset] = []
    return out


def run_engine(
    request: RunRequest,
    price_source: PriceSource,
    deriv_source: DerivSource,
    llm: LLMClient,
) -> RunResult:
    ohlcv = _fetch_ohlcv(price_source, request.universe)
    funding = _fetch_funding(deriv_source, request.universe)

    ctx = AgentContext(
        request=request,
        data={"ohlcv": ohlcv, "funding": funding},
        llm=llm,
    )

    signals = []
    failed: list[str] = []
    for agent in TIER_A_AGENTS:
        try:
            signals.extend(agent.run(ctx))
        except Exception:
            failed.append(agent.name)

    pm_ctx = AgentContext(
        request=request,
        data={"upstream_signals": signals},
        llm=llm,
    )
    try:
        decisions = PortfolioManagerAgent().make_decisions(pm_ctx)
    except Exception:
        decisions = []
        failed.append("portfolio_manager")

    return RunResult(
        run_id=uuid.uuid4().hex[:12],
        as_of=request.as_of or datetime.now(timezone.utc),
        signals=signals,
        decisions=decisions,
        cost_usd=0.0,
        agents_failed=failed,
    )
```

- [ ] **Step 4: Run tests, expect pass**

Run:

```bash
pytest tests/test_graph_runner.py -v
```

Expected: `2 passed`.

- [ ] **Step 5: Commit**

```bash
git add engine/crypto_claw_engine/graph/ engine/tests/test_graph_runner.py
git commit -m "feat(engine): sequential run_engine wiring agents + degradation"
```

---

## Task 13: CLI Entry Point

**Files:**
- Create: `engine/crypto_claw_engine/__main__.py`
- Create: `engine/crypto_claw_engine/cli.py`
- Create: `engine/tests/test_cli.py`

**CLI shape:**
- `crypto-claw analyze --universe BTC,ETH,SOL [--horizon daily] [--portfolio-file path]`
- Uses live CoinGeckoAdapter and BinanceAdapter by default
- LLM defaults to FakeLLM (flag `--real-llm` deferred to M3)
- Prints: 1) human-readable summary per decision, 2) `--json` flag for structured dump
- Exit code 0 on success, 1 if all agents failed

- [ ] **Step 1: Write failing test**

Create `engine/tests/test_cli.py`:

```python
import json

from click.testing import CliRunner

from crypto_claw_engine.cli import main


def test_cli_analyze_runs_with_fakes(monkeypatch):
    # Inject fakes via env var sentinels that cli.py recognizes for tests.
    monkeypatch.setenv("CRYPTO_CLAW_FAKE_DATA", "1")
    runner = CliRunner()
    result = runner.invoke(main, ["analyze", "--universe", "BTC,ETH", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output.strip().splitlines()[-1])
    assert "decisions" in payload
    assert {d["asset"] for d in payload["decisions"]} == {"BTC", "ETH"}


def test_cli_human_summary(monkeypatch):
    monkeypatch.setenv("CRYPTO_CLAW_FAKE_DATA", "1")
    runner = CliRunner()
    result = runner.invoke(main, ["analyze", "--universe", "BTC"])
    assert result.exit_code == 0
    assert "BTC" in result.output
    assert "Decision" in result.output or "decision" in result.output.lower()
```

- [ ] **Step 2: Run, expect fail**

Run:

```bash
pytest tests/test_cli.py -v
```

Expected: `ImportError` or `AttributeError`.

- [ ] **Step 3: Implement cli.py and __main__.py**

Create `engine/crypto_claw_engine/__main__.py`:

```python
from crypto_claw_engine.cli import main

if __name__ == "__main__":
    main()
```

Create `engine/crypto_claw_engine/cli.py`:

```python
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import click

from crypto_claw_engine.data.base import DerivSnapshot, OHLCVBar
from crypto_claw_engine.data.binance import BinanceAdapter
from crypto_claw_engine.data.coingecko import CoinGeckoAdapter
from crypto_claw_engine.graph.runner import run_engine
from crypto_claw_engine.llm import FakeLLM
from crypto_claw_engine.models import Portfolio, RunRequest


def _fake_price_source():
    class FakePrice:
        def get_ohlcv(self, asset, interval, limit):
            base = datetime(2026, 1, 1, tzinfo=timezone.utc)
            return [
                OHLCVBar(
                    open_time=base + timedelta(days=i),
                    open=100 + i,
                    high=100 + i + 1,
                    low=100 + i - 1,
                    close=100 + i * 1.5,
                    volume=10.0,
                )
                for i in range(80)
            ]

    return FakePrice()


def _fake_deriv_source():
    class FakeDeriv:
        def get_funding(self, asset, limit):
            return [
                DerivSnapshot(
                    symbol=f"{asset}USDT",
                    funding_rate=0.0005,
                    as_of=datetime(2026, 1, 1, tzinfo=timezone.utc),
                )
                for _ in range(10)
            ]

    return FakeDeriv()


def _load_portfolio(path: str | None) -> Portfolio:
    if not path:
        return Portfolio(cash_usd=10_000.0)
    data = json.loads(Path(path).read_text())
    return Portfolio(**data)


@click.group()
def main():
    """AI-Crypto-Claw engine CLI."""


@main.command()
@click.option("--universe", required=True, help="Comma-separated ticker list, e.g. BTC,ETH,SOL")
@click.option("--horizon", default="daily", type=click.Choice(["intraday", "daily", "weekly"]))
@click.option("--portfolio-file", default=None, help="Path to portfolio JSON file")
@click.option("--json", "as_json", is_flag=True, help="Dump machine-readable JSON")
def analyze(universe, horizon, portfolio_file, as_json):
    """Run the council against the given universe and print decisions."""
    assets = [a.strip().upper() for a in universe.split(",") if a.strip()]
    portfolio = _load_portfolio(portfolio_file)
    request = RunRequest(universe=assets, horizon=horizon, portfolio=portfolio)

    if os.environ.get("CRYPTO_CLAW_FAKE_DATA") == "1":
        price_source = _fake_price_source()
        deriv_source = _fake_deriv_source()
    else:
        price_source = BinanceAdapter()  # used for klines
        deriv_source = BinanceAdapter()  # used for funding
        _ = CoinGeckoAdapter()  # imported for future price enrichment; no-op in M1

    result = run_engine(
        request=request,
        price_source=price_source,
        deriv_source=deriv_source,
        llm=FakeLLM(),
    )

    if as_json:
        click.echo(result.model_dump_json())
        return

    click.echo(f"\n=== AI-Crypto-Claw run {result.run_id} @ {result.as_of.isoformat()} ===\n")
    for d in result.decisions:
        action_upper = d.action.upper()
        click.echo(f"Decision: {d.asset} {action_upper}  size={d.size_pct:+.2f}  conf={d.confidence:.2f}")
        click.echo(f"  reasoning: {d.reasoning}")
        for s in d.contributing_signals:
            click.echo(f"    [{s.agent}] {s.stance}  conf={s.confidence:.2f}  {s.rationale[:80]}")
        click.echo("")
    if result.agents_failed:
        click.echo(f"agents_failed: {result.agents_failed}")
```

- [ ] **Step 4: Run CLI tests**

Run:

```bash
pytest tests/test_cli.py -v
```

Expected: `2 passed`.

- [ ] **Step 5: Run CLI manually against fake data**

Run:

```bash
CRYPTO_CLAW_FAKE_DATA=1 python -m crypto_claw_engine analyze --universe BTC,ETH,SOL
```

Expected: prints `=== AI-Crypto-Claw run ... ===` followed by 3 Decision blocks (BTC, ETH, SOL), each with contributing signals from technicals / derivatives / tail_risk.

- [ ] **Step 6: Commit**

```bash
git add engine/crypto_claw_engine/cli.py engine/crypto_claw_engine/__main__.py engine/tests/test_cli.py
git commit -m "feat(engine): click CLI with analyze command (fake + live)"
```

---

## Task 14: Live Golden Path Integration Test

**Files:**
- Create: `engine/tests/test_live_golden_path.py`

This test actually hits CoinGecko + Binance. Marked `@pytest.mark.live` so `pytest` skips it by default; run with `pytest -m live`.

- [ ] **Step 1: Write the live test**

Create `engine/tests/test_live_golden_path.py`:

```python
import pytest

from crypto_claw_engine.data.binance import BinanceAdapter
from crypto_claw_engine.graph.runner import run_engine
from crypto_claw_engine.llm import FakeLLM
from crypto_claw_engine.models import Portfolio, RunRequest


@pytest.mark.live
def test_live_btc_eth_run_produces_decisions():
    adapter = BinanceAdapter()
    req = RunRequest(universe=["BTC", "ETH"], portfolio=Portfolio(cash_usd=10_000.0))
    result = run_engine(
        request=req,
        price_source=adapter,
        deriv_source=adapter,
        llm=FakeLLM(),
    )

    assert len(result.decisions) == 2
    assert {d.asset for d in result.decisions} == {"BTC", "ETH"}
    # Expect technicals + derivatives + tail_risk per asset = 6 signals total.
    assert len(result.signals) == 6
    # At least derivatives should return non-zero confidence on live data.
    live_conf_signals = [s for s in result.signals if s.confidence > 0]
    assert len(live_conf_signals) >= 2
    assert not result.agents_failed
```

- [ ] **Step 2: Run it live**

Run:

```bash
pytest tests/test_live_golden_path.py -m live -v
```

Expected: `1 passed`. Network required.

- [ ] **Step 3: Run the full suite one final time**

Run:

```bash
pytest -v
pytest -m live -v
```

Expected: all unit tests pass, live test passes.

- [ ] **Step 4: Run CLI against real APIs**

Run:

```bash
python -m crypto_claw_engine analyze --universe BTC,ETH,SOL
```

Expected: real decisions printed with real evidence fields (non-fake RSI, ATR, funding values from Binance).

- [ ] **Step 5: Commit**

```bash
git add engine/tests/test_live_golden_path.py
git commit -m "test(engine): live golden path against Binance (marked live)"
```

---

## Self-Review Checklist (run before handing off)

1. **Spec coverage:** §6 of the spec lists 8 concrete in-scope items. Map each to tasks:
   - Engine package skeleton → Task 1
   - Pydantic schemas → Task 2
   - LLM Protocol + FakeLLM → Task 3
   - CoinGecko + Binance adapters → Tasks 5, 6
   - 4 agents (Technicals/Derivatives/TailRisk/PM) → Tasks 8, 9, 10, 11
   - LangGraph-structured orchestration → Task 12 (sequential stand-in; full parallel DAG in M2, noted in Task 12 body)
   - CLI entry point → Task 13
   - Unit tests + live integration test → every task has TDD steps; Task 14 is the live golden path
   - ✅ All covered.

2. **Placeholders:** grep for TBD / TODO / "fill in" / "similar to" — none present.

3. **Type consistency:** `AgentSignal`, `Decision`, `RunRequest`, `RunResult`, `Portfolio`, `AgentContext`, `DataGap`, `PriceSource`, `DerivSource`, `LLMClient` — all defined once and reused with matching signatures across tasks.

4. **Scope:** engine only, no shells. Matches §6 exactly. No accidental creep.

---

## Running Tally of Commits

Task 1  → `feat(engine): project skeleton with smoke test`
Task 2  → `feat(engine): pydantic schemas and error types`
Task 3  → `feat(engine): LLMClient protocol and FakeLLM`
Task 4  → `feat(engine): data source protocols and domain types`
Task 5  → `feat(engine): CoinGecko price adapter with DataGap on failure`
Task 6  → `feat(engine): Binance public REST adapter (klines, funding, OI)`
Task 7  → `feat(engine): AgentBase and AgentContext`
Task 8  → `feat(engine): TechnicalsAgent with RSI/ATR/trend features`
Task 9  → `feat(engine): DerivativesAgent based on funding rate`
Task 10 → `feat(engine): TailRiskAgent with vol regime and drawdown`
Task 11 → `feat(engine): PortfolioManagerAgent with consensus-based decisions`
Task 12 → `feat(engine): sequential run_engine wiring agents + degradation`
Task 13 → `feat(engine): click CLI with analyze command (fake + live)`
Task 14 → `test(engine): live golden path against Binance (marked live)`

14 commits, ~17 bite-sized steps per big task, one merge-clean engine package at the end.
