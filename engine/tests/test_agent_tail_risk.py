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
    closes = [100] * 40 + [80 - i for i in range(30)]
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
