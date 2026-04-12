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
