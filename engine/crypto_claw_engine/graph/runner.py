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
