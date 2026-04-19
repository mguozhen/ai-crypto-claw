"""
Reflection Agent — reviews recent trade history and outputs strategy adjustment signals.
Inspired by CryptoTrade (EMNLP 2024).
"""
import os
import json
from crypto_claw_engine.agents.base import AgentBase, AgentContext
from crypto_claw_engine.models import AgentSignal


class ReflectionAgent(AgentBase):
    name = "reflection"

    def analyze(self, asset: str, ctx: AgentContext) -> AgentSignal:
        # Load trade journal if available
        journal_path = os.environ.get("TRADE_JOURNAL_PATH", "")
        past_decisions = []
        if journal_path and os.path.exists(journal_path):
            try:
                with open(journal_path) as f:
                    journal = json.load(f)
                past_decisions = [
                    d for d in journal.get("decisions", [])
                    if d.get("asset") == asset
                ][-20:]  # Last 20 decisions for this asset
            except Exception:
                pass

        # Load semantic rules if available
        rules_path = os.environ.get("TRADE_RULES_PATH", "")
        rules = ""
        if rules_path and os.path.exists(rules_path):
            try:
                with open(rules_path) as f:
                    rules = f.read()
            except Exception:
                pass

        if not past_decisions:
            return AgentSignal(
                agent=self.name,
                asset=asset,
                stance="neutral",
                confidence=0.3,
                rationale="No historical decisions available for reflection.",
                evidence={"past_decisions": 0, "rules": "none"},
            )

        # Analyze past performance
        wins = [d for d in past_decisions if d.get("outcome") == "win"]
        losses = [d for d in past_decisions if d.get("outcome") == "loss"]
        win_rate = len(wins) / max(len(past_decisions), 1)

        # Determine stance based on historical performance
        if win_rate >= 0.6 and len(past_decisions) >= 5:
            last_action = past_decisions[-1].get("action", "hold")
            stance = "bullish" if last_action in ("buy", "long") else "bearish"
            confidence = min(0.8, win_rate)
            rationale = f"Historical win rate {win_rate:.0%} over {len(past_decisions)} decisions suggests continuing recent direction."
        elif win_rate <= 0.4 and len(past_decisions) >= 5:
            last_action = past_decisions[-1].get("action", "hold")
            stance = "bearish" if last_action in ("buy", "long") else "bullish"
            confidence = min(0.7, 1 - win_rate)
            rationale = f"Low win rate {win_rate:.0%} — consider reversing recent approach."
        else:
            stance = "neutral"
            confidence = 0.4
            rationale = f"Win rate {win_rate:.0%} is inconclusive. Insufficient pattern."

        if rules:
            rationale += f" Active rules: {rules[:200]}"

        return AgentSignal(
            agent=self.name,
            asset=asset,
            stance=stance,
            confidence=confidence,
            rationale=rationale,
            evidence={
                "past_decisions": len(past_decisions),
                "win_rate": round(win_rate, 2),
                "wins": len(wins),
                "losses": len(losses),
                "has_rules": bool(rules),
            },
        )
