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
    assert len(result.signals) == 3
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

    neutral_zero = [
        s for s in result.signals if s.stance == "neutral" and s.confidence == 0.0
    ]
    assert len(neutral_zero) >= 2
    assert any(s.agent == "derivatives" and s.confidence > 0 for s in result.signals)
