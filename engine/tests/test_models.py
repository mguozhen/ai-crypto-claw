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
