from crypto_claw_engine.agents.base import AgentBase, AgentContext
from crypto_claw_engine.models import AgentSignal


class DerivativesAgent(AgentBase):
    name = "derivatives"

    def analyze(self, asset: str, ctx: AgentContext) -> AgentSignal:
        snaps = (ctx.data.get("funding") or {}).get(asset) or []
        if not snaps:
            return AgentSignal(
                agent=self.name,
                asset=asset,
                stance="neutral",
                confidence=0.0,
                rationale="Data unavailable (no funding snapshots).",
                evidence={"snapshots": 0},
            )

        rates = [s.funding_rate for s in snaps]
        avg = sum(rates) / len(rates)

        stance = "neutral"
        confidence = 0.5
        if avg > 0.0003:
            stance = "bearish"
            confidence = min(0.5 + avg * 500, 0.95)
        elif avg < -0.0001:
            stance = "bullish"
            confidence = min(0.5 + abs(avg) * 500, 0.95)

        evidence = {
            "avg_funding": round(float(avg), 6),
            "snapshots": len(rates),
            "latest_funding": round(float(rates[-1]), 6),
        }

        rationale = (
            ctx.llm.complete(
                messages=[
                    {
                        "role": "user",
                        "content": f"Assess {asset} derivatives: {evidence}. Stance: {stance}.",
                    }
                ],
                tag="derivatives",
            )
            if ctx.llm
            else f"{asset} derivatives {stance}; evidence: {evidence}"
        )

        return AgentSignal(
            agent=self.name,
            asset=asset,
            stance=stance,
            confidence=confidence,
            rationale=rationale,
            evidence=evidence,
        )
