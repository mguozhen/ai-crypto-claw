"""
Engine runner — DAG-based parallel execution.

Layer 0 (parallel): Technicals + Derivatives + TailRisk + Reflection
Layer 1 (parallel): BullResearcher + BearResearcher
Layer 2: PortfolioManager (final decision)
"""
import uuid
from datetime import datetime, timezone

from crypto_claw_engine.agents.base import AgentContext
from crypto_claw_engine.agents.derivatives import DerivativesAgent
from crypto_claw_engine.agents.portfolio_manager import PortfolioManagerAgent
from crypto_claw_engine.agents.tail_risk import TailRiskAgent
from crypto_claw_engine.agents.technicals import TechnicalsAgent
from crypto_claw_engine.agents.reflection import ReflectionAgent
from crypto_claw_engine.agents.debate import BullResearcher, BearResearcher
from crypto_claw_engine.data.base import DerivSource, PriceSource
from crypto_claw_engine.graph.dag_runner import DAGRunner
from crypto_claw_engine.llm import LLMClient
from crypto_claw_engine.models import RunRequest, RunResult


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

    # DAG execution: layer 0 → layer 1 → layer 2
    agents_by_layer = {
        0: [TechnicalsAgent(), DerivativesAgent(), TailRiskAgent(), ReflectionAgent()],
        1: [BullResearcher(), BearResearcher()],
    }

    dag = DAGRunner(max_workers=4)
    signals, failed = dag.run_agents(agents_by_layer, ctx)

    # Layer 2: Portfolio Manager (needs all signals + debate results)
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
