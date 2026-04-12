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
