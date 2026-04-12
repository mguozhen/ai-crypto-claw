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
