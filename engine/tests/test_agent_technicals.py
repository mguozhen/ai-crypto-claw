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
    closes = [100 + i * 2 for i in range(30)]
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
