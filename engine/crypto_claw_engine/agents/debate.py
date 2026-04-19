"""
Bull/Bear Debate Agents — inspired by TradingAgents.
Two researchers argue before the PM makes a final decision.
"""
from crypto_claw_engine.agents.base import AgentBase, AgentContext
from crypto_claw_engine.models import AgentSignal


class BullResearcher(AgentBase):
    name = "bull_researcher"

    def analyze(self, asset: str, ctx: AgentContext) -> AgentSignal:
        upstream = ctx.data.get("upstream_signals", [])
        asset_signals = [s for s in upstream if s.asset == asset]

        # Collect bullish evidence
        bullish_points = []
        for sig in asset_signals:
            if sig.stance == "bullish":
                bullish_points.append(f"[{sig.agent}] {sig.rationale} (conf={sig.confidence:.0%})")
            elif sig.stance == "neutral":
                # Find anything positive in neutral signals
                bullish_points.append(f"[{sig.agent}] Neutral but no bearish pressure: {sig.rationale[:80]}")

        if not bullish_points:
            bullish_points = ["No strong bullish signals from upstream, but absence of bearish consensus suggests floor."]

        rationale = (
            f"BULL CASE for {asset}: "
            + " | ".join(bullish_points[:5])
            + " — Recommend maintaining or increasing exposure."
        )

        # Bull confidence based on how many upstream agents agree
        bullish_count = sum(1 for s in asset_signals if s.stance == "bullish")
        confidence = min(0.9, 0.3 + bullish_count * 0.2)

        return AgentSignal(
            agent=self.name,
            asset=asset,
            stance="bullish",
            confidence=confidence,
            rationale=rationale,
            evidence={
                "bullish_signals": bullish_count,
                "total_signals": len(asset_signals),
                "key_arguments": bullish_points[:3],
            },
        )


class BearResearcher(AgentBase):
    name = "bear_researcher"

    def analyze(self, asset: str, ctx: AgentContext) -> AgentSignal:
        upstream = ctx.data.get("upstream_signals", [])
        asset_signals = [s for s in upstream if s.asset == asset]

        # Collect bearish evidence
        bearish_points = []
        for sig in asset_signals:
            if sig.stance == "bearish":
                bearish_points.append(f"[{sig.agent}] {sig.rationale} (conf={sig.confidence:.0%})")
            elif sig.stance == "neutral":
                bearish_points.append(f"[{sig.agent}] Neutral signals mask underlying weakness: {sig.rationale[:80]}")

        if not bearish_points:
            bearish_points = ["No strong bearish signals, but caution warranted in current macro environment."]

        rationale = (
            f"BEAR CASE for {asset}: "
            + " | ".join(bearish_points[:5])
            + " — Recommend reducing exposure or hedging."
        )

        bearish_count = sum(1 for s in asset_signals if s.stance == "bearish")
        confidence = min(0.9, 0.3 + bearish_count * 0.2)

        return AgentSignal(
            agent=self.name,
            asset=asset,
            stance="bearish",
            confidence=confidence,
            rationale=rationale,
            evidence={
                "bearish_signals": bearish_count,
                "total_signals": len(asset_signals),
                "key_arguments": bearish_points[:3],
            },
        )
