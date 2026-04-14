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
    assert len(result.signals) == 6
    live_conf_signals = [s for s in result.signals if s.confidence > 0]
    assert len(live_conf_signals) >= 2
    assert not result.agents_failed
